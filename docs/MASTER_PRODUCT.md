# Storyline news product blueprint

Draft · 21 October 2026 · Working name subject to availability checks

## Product direction

Develop the existing news scraper into **Storyline**, a news reader built around short explanations and continuing stories. Inshorts is the reference for convenient reading. Storyline's proposed signature experience remembers which version of a story a reader has seen and shows substantive developments when they return.

**Promise: Catch up on the stories you follow without rereading yesterday's news.**

The core remains news collection, aggregation, summarization, discovery, and reading. Begin with Indian business and technology for busy professionals, in English. This audience is a testable starting choice that suits the current sources. Expand to general news and other languages when demand and editorial capacity justify it.

The product serves three situations: discovering a story, checking a new development, and returning after several days away. It should make each feel easy while keeping original sources accessible.

## Competitive position

| Reference | Publicly described strength | Implication |
|---|---|---|
| Inshorts | Short summaries, personalization and category browsing | Convenient short cards are familiar, but insufficient differentiation |
| Ground News | Comparing headlines, coverage and perspectives across sources | Source comparison is already an established feature |
| Particle | Groups coverage into stories; offers summaries, questions, following and audio | Adding AI chat and summaries alone will not create a distinctive product |

Sources checked 21 October 2026: [Inshorts](https://inshorts.com/), [Ground News](https://ground.news/product), [Particle](https://particle.news/blog/introducing-particle-the-news-organized).

The differentiation hypothesis is the combination of **a finite daily briefing, a personal record of story versions read, and a reliable explanation of what changed**, with depth on Indian business and technology. This research does not establish that competitors lack similar features. Validate reader preference rather than claiming a new category.

Avoid promises of perfectly unbiased news, automated truth detection, exhaustive coverage or instant publication. Make attribution, disagreements, corrections and coverage limitations visible.

## Signature features

### One story with its sources

Several reports about the same event become one story card, with a concise summary, timestamps, relevant entities and source links. Readers can expand the coverage instead of encountering the same event repeatedly in the main feed.

Distinguish article count from independent reporting. Ten republications of a wire report do not constitute ten independent confirmations. Articles about the same company can concern different events and should remain separate.

### Short first read with deeper context

Default to approximately 60–90 words when the evidence supports it. Put background and a timeline beneath the summary. Do not pad thin evidence to meet a word target.

Every factual summary statement needs traceable evidence. The current headline-only inputs cannot reliably support detailed summaries. Until permitted source text is available, show an attributed headline and link rather than inventing context.

### Since you last read

Compare the latest supported story version against the version the reader marked read. Show new facts, changed dates, decisions, corrections and reversals. Another publisher repeating an existing claim should not create an update.

Use an explicit Mark read control. Opening a card briefly should not automatically hide information. The stored read version represents a user preference, not proof of comprehension.

### A briefing with an ending

Start with a five-minute daily briefing, based on estimated reading times. Give it a completion state and an optional route to explore more. Separate major general developments from selected interests so personalization does not remove all broader context.

Explain why stories appear, keep topic choices editable, and avoid optimizing for outrage or longer sessions.

### Follow meaningful developments

Let readers follow stories, companies and topics. Notify only on substantive changes, with digest frequency and quiet-hour controls. Show successful checks with no updates differently from collection failures.

### Reported facts and unresolved questions

Show specific disagreements with attribution. Distinguish a company's statement from an independently established fact. Source agreement alone does not prove truth.

Corrections create visible revisions. Readers who saw an erroneous version should receive the correction in their update queue, even after completing their daily briefing.

## Example reading session

The following acquisition story is fictional.

A reader opens a card explaining that Northstar Software announced an acquisition. They read the brief, open its sources, follow the story and mark the version read.

Two days later, the board approves the transaction. Five outlets repeat the announcement. Storyline shows one update: **The board has approved the transaction. Regulatory approval remains pending.** The reader can inspect the new sources or reopen the complete timeline.

After a week away, the reader chooses Catch me up and sees the developments since their saved version. The system does not make them restart with the original announcement.

This is the defining demonstration: one evolving story, several sources, and a different catch-up experience depending on what the reader has already seen.

## First version

| Build first | Acceptance condition |
|---|---|
| Curated news sources | Access method, source health and timestamps are recorded |
| Persistent article and story records | Refresh preserves prior versions |
| Exact deduplication and reviewed event clustering | Related coverage groups without merging distinct events |
| Short cited summaries | Factual statements can be checked against retrieved material |
| Story timeline and version comparison | A substantial development produces a supported change summary |
| Follow and Mark read | Subsequent visits compare against the correct saved version |
| Finite daily briefing | Readers can complete it and inspect its coverage |
| Correction and editorial review tools | Mistakes can be repaired without manipulating raw files |

After this loop works, test personalized audio, Hindi summaries with editorial review, source comparison, and questions grounded in a story's documents. An unanswered question should remain unanswered when evidence is insufficient.

Defer native mobile apps, social comments, creator publishing, a public news API, investment recommendations, automated bias scores and broad local reporting. Begin with a mobile-friendly web experience; add installability when the reading flow is stable.

## How the existing project evolves

Keep Flask, the source configuration pattern, useful RSS and HTML adapters, structured model calls, readable typography, and light and dark themes.

The previously inspected local snapshot contained 392 displayed rows, including 59 extra occurrences of exact normalized headlines. Its final schema lacked publication and collection timestamps. Those findings justify prioritizing deduplication and history before source count.

| Current component | Proposed change |
|---|---|
| `sources.py` | Record category, language, access method, attribution and health |
| Fetchers in `mainFile.py` | Preserve metadata and permitted content through source adapters |
| Stock/general classification | Topic and entity tagging across the chosen news scope |
| Buy/hold/sell output | Supported summaries, evidence references and update classification |
| `gemini_analyzer.py` | Extract cited claims and produce summaries with explicit abstention |
| Headline-only cache | Key by source content, prompt, schema and model versions |
| CSV storage | Persistent relational database; retain CSV for import/export |
| Synchronous refresh in `app.py` | Separate worker with locking, retries, job status and successful publication |
| `templates/index.html` | Story cards, source details, timelines and reader controls |
| `static/styles.css` | Preserve readability while improving mobile navigation |

Remove the stock-only display filter. A frontend framework rewrite is unnecessary until interaction needs justify it.

Basic robustness needs attention: the earlier local check found `/?page=abc` returns HTTP 500; refresh can appear successful after subprocess failure; concurrent refreshes can race on shared files. The displayed current date also does not establish article freshness.

## News engine

`Collect → preserve provenance → deduplicate → cluster events → extract cited claims → compare versions → review → publish → assemble reader briefing`

Core records: Source, Article, ArticleVersion, Story, StoryVersion, Claim, ClaimEvidence, Entity, Topic, ReaderStoryState, Follow, Briefing and Correction. Keep publication time, retrieval time, source modification time and story revision time separate. Unknown dates remain unknown.

Begin deduplication with canonical URLs and normalized titles. For event clustering, combine entities, time windows and semantic similarity with event checks. Preserve merge and split corrections. A shared company name is insufficient evidence to merge reports.

Compare supported claims rather than generated wording. Classify differences as new fact, corrected fact, changed status, changed date, duplicate coverage or editorial rewrite. Only substantive categories create reader updates. Store the evidence and versions used in every comparison.

Extract and summarize once per story revision, then reuse that work across readers. Personalization should mainly select, order and compare stored versions. Avoid regenerating every article for every person.

Review conflicts, weak evidence, ambiguous clusters and sensitive stories before publication. Retrieved text is untrusted content and cannot instruct the system or authorize actions. Protect private follows and read history with authentication, access controls and deletion options before launching accounts.

## Source feasibility

Audit 20–30 feeds or publisher pages and identify a smaller dependable set that can support summaries. Record access method, permitted content use, attribution requirements, refresh interval and failures. Source discovery is separate from reliable production ingestion.

RSS availability does not itself establish rights to republish full articles or images. Use licensed or otherwise permitted material, preserve attribution and links, and avoid bypassing paywalls. Omit images when permitted use is unclear.

Headline-only stories can remain attributed links. They should not receive invented explanations merely to fill a card. Display collection outages separately from an absence of news.

## Business model hypothesis

Provide a free daily briefing, citations, corrections and a limited number of followed stories. Test **₹199 per month** for extended follows, custom briefings and deeper personal catch-up history. Add audio as a paid convenience only after measuring demand and cost.

This price is an experiment, not demonstrated willingness to pay. Core source access and factual corrections should stay available to every reader. The paid promise is repeated time savings and control over what to follow.

Consumer news competes with many free alternatives. Recruit people who repeatedly follow developments for work, then test actual payment after use. Downloads and positive comments are insufficient evidence of a business.

Measure model and hosting costs per active reader, editorial minutes per published revision, licensing, payments and free-user support. Shared processing reduces some costs but does not eliminate editorial or content costs. Forecast margins only after measuring these inputs.

If readers return but will not pay individually, test professional topic editions or team briefings using the same news engine. Preserve news as the core product.

## Six week validation plan

| Period | Deliverable | Evidence sought |
|---|---|---|
| Week 1 | Ten reader interviews, source audit and sample cards | Repeated frustration with duplication or catching up, plus usable sources |
| Week 2 | Article history, deduplication, reviewed clusters and citations | A reliable small corpus that survives refreshes |
| Weeks 3 and 4 | Briefing, timeline, follow and read-version behavior | Readers complete the entire loop without builder assistance |
| Weeks 5 and 6 | A 30-reader pilot and paid continuation offer | Repeated use, less repeated reading, summary quality and payment |

Proposed internal gates: at least 12 of 30 readers return on three separate days in week four, and at least six accept paid continuation at the stated price. These small-sample thresholds guide investment; they are not industry benchmarks or achieved results.

Compare a conventional summary feed against the version-aware briefing on comparable story sets. Measure time to identify changes, simple comprehension checks, and perceived repetition. Use unseen stories to avoid teaching participants the evaluation examples.

Audit at least 100 summary claims and 50 update decisions against their underlying sources and histories. Require zero critical factual errors in the audited release sample; any such error blocks affected content until corrected. Track omissions, false updates and clustering errors separately. A clean sample does not guarantee perfect accuracy.

The central success behavior is a reader completing a useful briefing and returning for the next meaningful development. Track retention, successful catch-up sessions and paid renewal. Session length and notification volume are not success targets.

## Immediate next build

Implement one complete story flow: ingest several permitted reports on a real event, preserve them, produce one cited summary, record a reader marking it read, add a later development, and show only the supported change with access to the full timeline.

This exposes the difficult parts early: source text, event clustering, factual comparison and reader state. Expand to a daily briefing only after this flow works reliably.

The previous industrial proposal is archived in ARCHIVED_FIELDSIGNAL_PROPOSAL.md. This is the active blueprint. The application itself has not been changed by this revision.
