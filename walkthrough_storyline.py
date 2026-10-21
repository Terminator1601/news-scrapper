"""Replay the blueprint's example reading session on the real Jio IPO event.

Stage 1 attaches only pre-subscription coverage and generates version 1.
The reader marks it read. Stage 2 attaches the subscription coverage, which
should produce exactly one substantive update visible under "Since you last
read". Run: ./venv/bin/python walkthrough_storyline.py
"""

import json

import storyline

SUBSCRIBED_WORDS = ("subscrib",)  # matches subscribed / subscription

story_id = storyline.follow_event('jio-ipo', 'Reliance Jio IPO', ['jio', 'ipo'])

conn = storyline.connect()
conn.execute("DELETE FROM reader_story_state WHERE story_id = ?", (story_id,))
conn.execute("DELETE FROM story_versions WHERE story_id = ?", (story_id,))
conn.execute("DELETE FROM story_articles WHERE story_id = ?", (story_id,))
conn.commit()

matching = [a for a in conn.execute("SELECT * FROM articles").fetchall()
            if all(k in f"{a['title']} {a['description']}".lower()
                   for k in ('jio', 'ipo'))]
early = [a for a in matching
         if not any(w in a['title'].lower() for w in SUBSCRIBED_WORDS)]
for article in early:
    conn.execute(
        "INSERT INTO story_articles (story_id, article_id, added_at) VALUES (?, ?, ?)",
        (story_id, article['id'], storyline.now()))
conn.commit()
conn.close()

print(f"Stage 1: {len(early)} pre-subscription articles of {len(matching)} total")
version, created = storyline.refresh_story_version(story_id)
print(f"  v{version['rev']} ({version['change_kind']}): {version['summary'][:120]}...")

storyline.mark_read(story_id, version['id'])
print("  Reader marked v1 read")

added = storyline.update_story_articles(story_id)
print(f"Stage 2: {len(added)} subscription-wave articles join the story")
version2, created2 = storyline.refresh_story_version(story_id)
print(f"  update created: {created2}")
if created2:
    print(f"  v{version2['rev']} [{version2['change_kind']}]: {version2['change_note']}")

view = storyline.story_view(story_id)
print(f"Reader catch-up shows {len(view['updates'])} update(s):")
for update in view['updates']:
    print(f"  [{update['change_kind']}] {update['change_note']}")
