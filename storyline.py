"""Storyline: persistent story records with cited summaries and versions.

First slice of docs/MASTER_PRODUCT.md: articles and stories live in SQLite,
refreshes preserve prior versions, one followed event produces a cited
summary, and a later development yields exactly one supported change.
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

import feedparser
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from sources import news_sources
from mainFile import REQUEST_HEADERS, fetch_headlines

load_dotenv()

DB_FILE = "./storyline.db"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    source_name TEXT NOT NULL,
    access TEXT NOT NULL,           -- 'rss' (permitted text) or 'html' (headline+link only)
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    title_norm TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    published_at TEXT,              -- source-declared time; NULL when unknown
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    keywords TEXT NOT NULL,         -- JSON list defining the followed event
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS story_articles (
    story_id INTEGER NOT NULL REFERENCES stories(id),
    article_id INTEGER NOT NULL REFERENCES articles(id),
    added_at TEXT NOT NULL,
    PRIMARY KEY (story_id, article_id)
);
CREATE TABLE IF NOT EXISTS story_versions (
    id INTEGER PRIMARY KEY,
    story_id INTEGER NOT NULL REFERENCES stories(id),
    rev INTEGER NOT NULL,
    status TEXT NOT NULL,           -- 'ok' or 'insufficient'
    summary TEXT NOT NULL,
    claims TEXT NOT NULL,           -- JSON [{text, evidence_ids}]
    change_kind TEXT NOT NULL,      -- 'initial', 'new_fact', 'changed_status', ...
    change_note TEXT NOT NULL,
    evidence TEXT NOT NULL,         -- JSON snapshot of article ids used
    created_at TEXT NOT NULL,
    UNIQUE (story_id, rev)
);
CREATE TABLE IF NOT EXISTS reader_story_state (
    story_id INTEGER PRIMARY KEY REFERENCES stories(id),
    read_version_id INTEGER NOT NULL REFERENCES story_versions(id),
    marked_at TEXT NOT NULL
);
"""

SUBSTANTIVE_KINDS = {"initial", "new_fact", "corrected_fact",
                     "changed_status", "changed_date"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def canonical_url(url):
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), '', ''))


def normalize_title(title):
    return re.sub(r'[^a-z0-9 ]', '', title.lower()).strip()


# ---------------------------------------------------------------- ingestion

def collect_articles(only_sources=None):
    """Fetch current items from configured sources into the articles table.

    Existing articles (same canonical URL or same source+normalized title)
    only get last_seen_at bumped: refreshes preserve prior records.
    Returns the number of newly inserted articles.
    """
    conn = connect()
    inserted = 0
    for source_name, info in news_sources.items():
        if only_sources is not None and source_name not in only_sources:
            continue
        for item in _fetch_source_items(source_name, info):
            if _upsert_article(conn, item):
                inserted += 1
    conn.commit()
    conn.close()
    return inserted


def _fetch_source_items(source_name, info):
    items = []
    if info.get("type") == "rss":
        try:
            response = requests.get(info["url"], headers=REQUEST_HEADERS, timeout=20)
            if response.status_code != 200:
                print(f"Storyline: failed to fetch {info['url']} (status {response.status_code})")
                return items
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                title = (entry.get("title") or "").strip()
                link = entry.get("link") or ""
                if not title or not link:
                    continue
                published = None
                if entry.get("published_parsed"):
                    published = datetime(*entry.published_parsed[:6],
                                         tzinfo=timezone.utc).isoformat(timespec="seconds")
                items.append({
                    "source_name": source_name, "access": "rss",
                    "url": link, "title": title,
                    "description": re.sub(r'<[^>]+>', '', entry.get("summary", "")).strip(),
                    "published_at": published,
                })
        except requests.exceptions.RequestException as error:
            print(f"Storyline: error fetching {info['url']}: {error}")
    else:
        for element in fetch_headlines(info):
            title = element.get_text().strip()
            anchor = element.find('a') or element.find_parent('a')
            if not title or len(title.split()) <= 2 or not anchor or 'href' not in anchor.attrs:
                continue
            from urllib.parse import urljoin
            items.append({
                "source_name": source_name, "access": "html",
                "url": urljoin(info["url"], anchor['href']), "title": title,
                "description": "", "published_at": None,
            })
    return items


def _upsert_article(conn, item):
    url = canonical_url(item["url"])
    title_norm = normalize_title(item["title"])
    if not title_norm:
        return False
    existing = conn.execute(
        "SELECT id FROM articles WHERE url = ? OR (source_name = ? AND title_norm = ?)",
        (url, item["source_name"], title_norm)).fetchone()
    timestamp = now()
    if existing:
        conn.execute("UPDATE articles SET last_seen_at = ? WHERE id = ?",
                     (timestamp, existing["id"]))
        return False
    conn.execute(
        """INSERT INTO articles (source_name, access, url, title, title_norm,
           description, published_at, first_seen_at, last_seen_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item["source_name"], item["access"], url, item["title"], title_norm,
         item["description"], item["published_at"], timestamp, timestamp))
    return True


# ---------------------------------------------------------------- clustering

def follow_event(slug, title, keywords):
    """Create (or fetch) a followed story defined by matching keywords."""
    conn = connect()
    row = conn.execute("SELECT id FROM stories WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO stories (slug, title, keywords, created_at) VALUES (?, ?, ?, ?)",
            (slug, title, json.dumps(keywords), now()))
        conn.commit()
        row = conn.execute("SELECT id FROM stories WHERE slug = ?", (slug,)).fetchone()
    story_id = row["id"]
    conn.close()
    return story_id


def update_story_articles(story_id):
    """Attach matching articles to the story. Returns ids of newly added articles."""
    conn = connect()
    story = conn.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
    keywords = [k.lower() for k in json.loads(story["keywords"])]
    added = []
    for article in conn.execute("SELECT * FROM articles").fetchall():
        haystack = f"{article['title']} {article['description']}".lower()
        if all(keyword in haystack for keyword in keywords):
            done = conn.execute(
                "SELECT 1 FROM story_articles WHERE story_id = ? AND article_id = ?",
                (story_id, article["id"])).fetchone()
            if not done:
                conn.execute(
                    "INSERT INTO story_articles (story_id, article_id, added_at) VALUES (?, ?, ?)",
                    (story_id, article["id"], now()))
                added.append(article["id"])
    conn.commit()
    conn.close()
    return added


# ------------------------------------------------------- summary and changes

class Claim(BaseModel):
    text: str
    evidence_ids: list[int]


class StorySummary(BaseModel):
    status: Literal["ok", "insufficient"]
    summary: str
    claims: list[Claim]


class ChangeAssessment(BaseModel):
    change_kind: Literal["new_fact", "corrected_fact", "changed_status",
                         "changed_date", "duplicate_coverage", "editorial_rewrite"]
    change_note: str


SUMMARY_PROMPT = """You summarize one news story for a reader, using ONLY the
evidence below. Each evidence item has an id, a source, a headline, and
sometimes a description. Items marked access=html provide only their headline.

Write a 60-90 word neutral summary of the event if the evidence supports one.
Attribute statements to their sources where relevant. List each factual claim
with the evidence ids that support it. Do not add background knowledge that is
not in the evidence. If the evidence is too thin for a real summary (for
example a single bare headline), set status to "insufficient" and leave
summary as one sentence noting what the sources report.

Evidence:
"""

CHANGE_PROMPT = """A reader already saw the PREVIOUS claims about this story.
Compare the NEW claims against them and classify the single most important
difference:
- new_fact: a substantive development the previous claims did not contain
- corrected_fact: a previous claim is contradicted or corrected
- changed_status: the event moved to a new stage (approved, completed, blocked)
- changed_date: a date or deadline changed
- duplicate_coverage: more sources repeat what was already known
- editorial_rewrite: wording changed, substance identical

change_note: one sentence a reader should see, describing only what changed.
For duplicate_coverage or editorial_rewrite, say no substantive change.

PREVIOUS claims:
{previous}

NEW claims:
{new}
"""


def _evidence_block(conn, story_id):
    rows = conn.execute(
        """SELECT a.* FROM articles a
           JOIN story_articles sa ON sa.article_id = a.id
           WHERE sa.story_id = ? ORDER BY a.first_seen_at""", (story_id,)).fetchall()
    lines = []
    for article in rows:
        line = (f"id={article['id']} source={article['source_name']} "
                f"access={article['access']} headline={article['title']!r}")
        if article["description"]:
            line += f" description={article['description'][:400]!r}"
        lines.append(line)
    return rows, "\n".join(lines)


def _gemini(contents, schema):
    if not os.environ.get("GEMINI_API_KEY"):
        return None
    from google import genai
    client = genai.Client()
    response = client.models.generate_content(
        model=GEMINI_MODEL, contents=contents,
        config={"response_mime_type": "application/json", "response_schema": schema})
    return response.parsed


def refresh_story_version(story_id):
    """Regenerate the story summary; record a new version only when substantive.

    Returns (version_row, created): the latest version and whether this call
    added one.
    """
    conn = connect()
    articles, evidence_text = _evidence_block(conn, story_id)
    if not articles:
        conn.close()
        return None, False

    latest = conn.execute(
        "SELECT * FROM story_versions WHERE story_id = ? ORDER BY rev DESC LIMIT 1",
        (story_id,)).fetchone()
    evidence_ids = [a["id"] for a in articles]
    if latest and json.loads(latest["evidence"]) == evidence_ids:
        conn.close()
        return latest, False  # nothing new to assess

    summary = _gemini(SUMMARY_PROMPT + evidence_text, StorySummary)
    if summary is None:
        conn.close()
        raise RuntimeError("GEMINI_API_KEY is not set; Storyline summaries need it.")

    claims_json = json.dumps([claim.model_dump() for claim in summary.claims],
                             ensure_ascii=False)
    if latest is None:
        change_kind, change_note = "initial", "First version of this story."
    else:
        assessment = _gemini(
            CHANGE_PROMPT.format(previous=latest["claims"], new=claims_json),
            ChangeAssessment)
        change_kind, change_note = assessment.change_kind, assessment.change_note
        if change_kind not in SUBSTANTIVE_KINDS:
            # More coverage, same facts: record nothing, the reader sees no update
            conn.close()
            return latest, False

    rev = (latest["rev"] + 1) if latest else 1
    conn.execute(
        """INSERT INTO story_versions (story_id, rev, status, summary, claims,
           change_kind, change_note, evidence, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (story_id, rev, summary.status, summary.summary, claims_json,
         change_kind, change_note, json.dumps(evidence_ids), now()))
    conn.commit()
    version = conn.execute(
        "SELECT * FROM story_versions WHERE story_id = ? AND rev = ?",
        (story_id, rev)).fetchone()
    conn.close()
    return version, True


# ------------------------------------------------------------- reader state

def mark_read(story_id, version_id):
    conn = connect()
    conn.execute(
        """INSERT INTO reader_story_state (story_id, read_version_id, marked_at)
           VALUES (?, ?, ?)
           ON CONFLICT(story_id) DO UPDATE SET read_version_id = ?, marked_at = ?""",
        (story_id, version_id, now(), version_id, now()))
    conn.commit()
    conn.close()


def story_view(story_id):
    """Everything the story page needs, including the since-you-read delta."""
    conn = connect()
    story = conn.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
    if story is None:
        conn.close()
        return None
    versions = conn.execute(
        "SELECT * FROM story_versions WHERE story_id = ? ORDER BY rev",
        (story_id,)).fetchall()
    articles, _ = _evidence_block(conn, story_id)
    state = conn.execute(
        "SELECT * FROM reader_story_state WHERE story_id = ?", (story_id,)).fetchone()
    conn.close()

    latest = versions[-1] if versions else None
    read_version = None
    updates = []
    if state and versions:
        read_version = next((v for v in versions
                             if v["id"] == state["read_version_id"]), None)
        if read_version:
            updates = [v for v in versions if v["rev"] > read_version["rev"]]
    return {
        "story": story, "versions": versions, "articles": articles,
        "latest": latest, "read_version": read_version, "updates": updates,
    }


def list_stories():
    conn = connect()
    rows = conn.execute(
        """SELECT s.*,
                  (SELECT COUNT(*) FROM story_articles sa WHERE sa.story_id = s.id) AS article_count,
                  (SELECT MAX(rev) FROM story_versions sv WHERE sv.story_id = s.id) AS latest_rev,
                  (SELECT rev FROM story_versions sv
                   JOIN reader_story_state r ON r.read_version_id = sv.id
                   WHERE r.story_id = s.id) AS read_rev
           FROM stories s ORDER BY s.created_at DESC""").fetchall()
    conn.close()
    return rows
