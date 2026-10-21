import hashlib
import json
import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
CACHE_FILE = "./headlines/analysis_cache.json"
BATCH_SIZE = 40

PROMPT = """You are labeling news headlines for a stock-market dashboard.
For each numbered headline decide:
- is_stock_market: true only if it concerns financial markets, listed companies,
  the economy, commodities, crypto, or investing. Crime, sports, politics or
  entertainment stories are false even if they mention money.
- signal: from a retail investor's perspective, whether the news suggests buying
  exposure to the affected company or sector (buy), reducing it (sell), or has no
  actionable direction (hold).
- company: the primary listed company or index the headline is about, or "" if none.
- rationale: one short sentence explaining the signal.

Headlines:
"""


class HeadlineAnalysis(BaseModel):
    id: int
    is_stock_market: bool
    signal: Literal["buy", "sell", "hold"]
    company: str = ""
    rationale: str = ""


def headline_key(headline):
    return hashlib.sha256(headline.strip().lower().encode("utf-8")).hexdigest()[:16]


def _load_cache():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return {}


def _save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=1)


def analyze_headlines(headlines):
    """Classify headlines with Gemini, caching by headline hash.

    Returns a dict mapping headline_key(headline) to
    {"is_stock_market": bool, "signal": str, "company": str, "rationale": str}.
    Headlines that could not be analyzed (no API key, API errors) are simply
    absent, so callers can fall back per headline.
    """
    cache = _load_cache()

    pending = []
    seen = set()
    for headline in headlines:
        key = headline_key(headline)
        if key not in cache and key not in seen:
            pending.append((key, headline.strip()))
            seen.add(key)

    if not pending:
        return cache

    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set; falling back to keyword analysis "
              f"for {len(pending)} new headlines (add it to .env to enable Gemini).")
        return cache

    from google import genai

    client = genai.Client()
    analyzed = 0
    for start in range(0, len(pending), BATCH_SIZE):
        batch = pending[start:start + BATCH_SIZE]
        numbered = "\n".join(f"{i}. {text}" for i, (_, text) in enumerate(batch))
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=PROMPT + numbered,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[HeadlineAnalysis],
                },
            )
            for item in response.parsed or []:
                if 0 <= item.id < len(batch):
                    key = batch[item.id][0]
                    cache[key] = {
                        "is_stock_market": item.is_stock_market,
                        "signal": item.signal,
                        "company": item.company.strip(),
                        "rationale": item.rationale.strip(),
                    }
                    analyzed += 1
        except Exception as error:  # noqa: BLE001 - any API failure falls back to keywords
            print(f"Gemini batch failed ({error}); keyword fallback will cover it.")

    _save_cache(cache)
    print(f"Gemini analyzed {analyzed} new headlines with {GEMINI_MODEL} "
          f"({len(cache)} total in cache).")
    return cache
