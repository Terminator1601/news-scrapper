"""Market Pulse assistant: answers from the scraped sources and the web.

Local headlines (storyline.db) are retrieved by keyword overlap and handed to
Gemini as primary evidence; Google Search grounding covers everything beyond
them. Falls back to a search-free call if grounding is unavailable.
"""

import os
import re
import sqlite3
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
DB_FILE = "./storyline.db"
MAX_HISTORY = 10
MAX_MESSAGE_CHARS = 2000

STOPWORDS = set(
    "the a an of to in on for and with as is are was were at by from after "
    "about what which when where who how why does did do can could should "
    "would latest today news tell me show happened happening".split())

SYSTEM_PROMPT = """You are the assistant inside Market Pulse, a personal
news dashboard that scrapes Indian and global business sources. Today is
{date}.

Ground your answers first in the headlines provided from the user's own
sources, attributing them by source name. Use web search for anything the
headlines do not cover, such as current prices, background, or breaking
developments, and say when information comes from the web. If neither covers
the question, say so instead of guessing. Keep answers short: a few sentences,
or a brief list when comparing items. Write plain text with no markdown
symbols such as ** or *. You are not a financial advisor; do not give
personalized investment advice."""


def _local_context(query, limit=12):
    words = [w for w in re.findall(r"[a-z0-9]+", query.lower())
             if w not in STOPWORDS and len(w) > 2]
    if not words:
        return []
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT source_name, title, description, url FROM articles").fetchall()
        conn.close()
    except sqlite3.Error:
        return []
    scored = []
    for row in rows:
        haystack = f"{row['title']} {row['description']}".lower()
        score = sum(haystack.count(word) for word in words)
        if score:
            scored.append((score, row))
    scored.sort(key=lambda pair: -pair[0])
    return [row for _, row in scored[:limit]]


def answer(messages):
    """messages: [{'role': 'user'|'bot', 'text': str}, ...], newest last."""
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("The assistant needs GEMINI_API_KEY in .env.")

    from google import genai

    cleaned = [
        {"role": "user" if m.get("role") == "user" else "model",
         "parts": [{"text": str(m.get("text", ""))[:MAX_MESSAGE_CHARS]}]}
        for m in messages[-MAX_HISTORY:] if str(m.get("text", "")).strip()
    ]
    if not cleaned or cleaned[-1]["role"] != "user":
        raise ValueError("The last message must be from the user.")

    query = cleaned[-1]["parts"][0]["text"]
    context_rows = _local_context(query)
    if context_rows:
        context = "\n".join(
            f"- [{row['source_name']}] {row['title']}"
            + (f" — {row['description'][:200]}" if row["description"] else "")
            for row in context_rows)
        cleaned[-1]["parts"][0]["text"] = (
            f"{query}\n\nHeadlines from my sources that may be relevant:\n{context}")

    client = genai.Client()
    config = {"system_instruction":
              SYSTEM_PROMPT.format(date=datetime.now().strftime("%A, %d %B %Y"))}
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=cleaned,
            config={**config, "tools": [{"google_search": {}}]})
    except Exception:
        # Search grounding unavailable: answer from sources and the model alone
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=cleaned, config=config)
    return (response.text or "").strip() or "I could not produce an answer. Try rephrasing."
