# Archived FieldSignal proposal

Superseded on 21 October 2026. The chosen direction remains news aggregation and reading. See MASTER_PRODUCT.md for the active blueprint. This earlier industrial supplier proposal is retained only as background.

## Product decision

Pivot Market Pulse into **FieldSignal**, an opportunity qualification service for industrial suppliers. It follows public project developments, matches them against a supplier's actual capabilities, and prepares an evidence-backed decision about what deserves sales attention.

**Customer promise:** Find projects worth investigating, understand why they fit your business, and see what you need to verify before spending time on them.

The initial market hypothesis is industrial water and wastewater treatment suppliers serving chemical manufacturers in Gujarat and Maharashtra. Start with owner-led vendors and small business-development teams. This segment and geography are proposed constraints, not validated demand. Customer access is a gate: if we cannot reach ten relevant buyers within two weeks, choose a reachable industrial niche before building.

The valuable unit is a **qualified project opportunity**, with explicit unknowns. News collection becomes one input to that product. The long-term ambition is a supplier's continuously maintained opportunity workspace, connecting project developments, requirements, capability evidence, and sales outcomes.

## What exists today

Market Pulse is a functioning Flask prototype. It collects HTML headings and RSS entries from 13 configured source endpoints, filters them, classifies them using Gemini or keyword fallback, writes CSV files, and renders a paginated dashboard with source filters, company labels, and buy/hold/sell badges. Its theme, readable layout, and structured model output are useful foundations.

The saved repository snapshot contains:

| Observation | Measured result | Product implication |
|---|---:|---|
| Raw rows collected | 1,041 | Collection works, but volume is not relevance |
| Rows surviving the short-headline filter | 806 | Broad page selectors collect substantial noise |
| Rows in the displayed stock dataset | 392 | The product is a feed, without a user-specific purpose |
| Extra occurrences of exact normalized headlines | 59 of 392, or 15.1% | Deduplication is an immediate improvement; event-level duplication may be higher |
| Blank company fields | 175 of 392, or 44.6% | Some items concern broad markets; these are not all extraction failures |
| Buy/sell rows with no company | 91 of 262, or 34.7% | Trading instructions can lack even an identified instrument |
| Rows matching a broad industrial discovery keyword set | 4 of 392 | The existing news sources cannot support the proposed niche on their own |

These counts describe local files, not verified live news. The keyword scan used plant, factory, commission, commissioning, capex, capacity, expansion, and tender. Its four matches were not qualified supplier opportunities.

The central product problem is that sentiment is being presented as a decision. A headline about expansion is insufficient evidence to recommend buying shares; equally, it is insufficient evidence that a supplier can win a contract. FieldSignal should preserve that distinction throughout its design.

## Why choose this direction

| Direction | Attractive aspect | Main obstacle | Decision |
|---|---|---|---|
| Improve the current market-news dashboard | Closest to existing code | Limited differentiation and weak support for trading calls | Keep only as the prototype foundation |
| Monitor investment theses | Useful recurring research task | Direct competitors already market this workflow | Do not lead with generic thesis monitoring |
| Track management promises and capex | More specific longitudinal data | Existing products cover guidance, commentary changes, and capex announcements | Possible later research vertical, not the initial bet |
| Qualify industrial opportunities for a specific supplier | Connects information to a business development decision and a potential budget | Requires specialist data, accurate matching, and customer access | Recommended paid pilot |

Ntree markets thesis conditions and source-linked monitoring. Quantalyze markets management credibility and quarterly commentary comparison. Tijori publishes capex announcements and company timelines. These are reasons to avoid claiming that adding memory or AI makes a market-news product novel. [Ntree](https://www.tryntree.com/), [Quantalyze](https://quantalyze.me/), [Tijori capex announcements](https://www.tijorifinance.com/ideas-dashboard/capex-announcement/).

Industrial opportunity intelligence also has substantial competition:

| Existing alternative | Capability described by the vendor | What FieldSignal must prove |
|---|---|---|
| Projects Today | Project stages, stakeholders, tenders, BOQ search, brand references, alerts, and activity tracking | A supplier-specific qualification workflow materially improves on the customer's existing process |
| Industrial Info Resources | Researched industrial project and plant intelligence | Useful coverage and dependable evidence in a deliberately small territory |
| ProjectX India | Curated project leads, tenders, awards, and expansions | Better follow-through and capability matching than a lead bulletin alone |
| Contify | Business monitoring, filtering, and manufacturing intelligence | A narrow workflow produces useful decisions with less setup for the target buyer |

Sources: [Projects Today](https://www.projectstoday.ai/), [Industrial Info Resources](https://www.industrialinfo.com/), [ProjectX India](https://projectxindia.com/access-project-leads-construction-infrastructure-projects-industrial-projects/), [Contify manufacturing](https://www.contify.com/industry/manufacturing/). These are public product descriptions, not independent performance tests.

**The differentiation hypothesis is the combination of a specific supplier's capabilities, disqualifying constraints, project history, evidence, and follow-through.** This research does not establish an empty market or prove competitors lack that combination. Validate it head-to-head with customer examples before making superiority claims. Lower price and AI summaries alone are not a defensible strategy.

## Customer and job to be done

The first buyer is an owner or sales leader at an industrial water-treatment supplier. The user is the person who spends time turning project announcements into possible accounts and checking whether the opportunity is real, reachable, and suitable.

Their recurring question is: **Which developments deserve my team's attention this week, given what we can actually deliver?**

During onboarding, record products and service scope, territories, preferred industries, commercial size range, relevant references, required approvals or certifications, and exclusions. The customer confirms these facts. A brochure can suggest fields, but extracted capabilities do not become verified capabilities automatically.

The product's first useful moment is a real project brief where the user can see the source, inspect the capability match, and identify one unanswered question. This should be achievable with a manually prepared brief before any substantial rebuild.

## Signature product experience

### Capability passport

A concise profile represents what the supplier sells, where it operates, and what it should decline. Each capability has an owner, confirmation date, and supporting customer-provided evidence where relevant. It can explicitly exclude municipal work, operation-only contracts, unsupported industries, or out-of-territory locations.

### Opportunity inbox

The home screen prioritizes projects whose evidence changed. Cards answer five questions: what changed, why it may fit, what is confirmed, what is missing, and what to verify next. A small relevant queue is more useful than a large daily quota.

Use four plain states: **Ready to investigate**, **Needs information**, **Outside your fit**, and **Watching**. These describe research readiness and customer fit, not purchase intent or likelihood of winning.

### Evidence and fit worksheet

Each criterion has two sides: evidence about the project and evidence about the supplier. The comparison yields match, mismatch, or unknown. Hard mismatches prevent an opportunity from appearing as ready. Missing project requirements remain unknown rather than receiving an optimistic score.

Examples include territory, industry, equipment or service scope, capacity range when documented, certifications when required, and buyer route. Each result links to its supporting passage or to the supplier's confirmation. Avoid a fabricated percentage probability of winning.

### Project memory

Announcements, approvals, appointments, tenders, and commissioning reports attach to the same project when identity is established. Preserve site, phase, dates, and changes instead of overwriting the previous state. An old story republished this week should not become a new lead.

Lifecycle stages are observed facts, not a mandatory linear progression. Approval does not imply funding, funding does not imply procurement is open, and silence does not prove cancellation. Conflicting dates appear together for review.

### Next verification step

Recommend a concrete research task: check whether a treatment package is in scope, identify the appointed engineering contractor from a public announcement, or confirm vendor registration requirements. Distinguish a publicly documented stakeholder from a suggested role to investigate.

### Outcome memory

The customer records already known, wrong fit, too early, research underway, conversation opened, RFQ received, or closed. Rejection reasons improve matching for that customer. Private customer outcomes must stay separate from shared public project records.

## Illustrative product walkthrough

The following company, project, dates, and figures are fictional product examples.

A supplier serves industrial wastewater projects in Gujarat and Maharashtra and excludes municipal contracts. FieldSignal receives three updates about the fictional **Nila Chemicals Dahej expansion**.

The first is a media announcement of a proposed expansion. The second is a hypothetical issuer document mentioning an effluent-treatment scope. The third names an engineering contractor. These become one project with three pieces of evidence.

The brief reads: **Treatment scope is documented. Territory and industry match your profile. Required treatment capacity and package procurement status are not established. Verify the engineering contractor's vendor process before treating this as an active sales opportunity.**

The worksheet shows location and industry as matches; treatment scope as potentially relevant; technical sizing, vendor eligibility, and procurement timing as unknown. A municipal project in the same region is suppressed because the supplier excludes that market.

When a new document changes the scope, the customer receives the change and its source. If nothing material changes, the project remains quiet. The supplier can record that the project was already known or no longer relevant.

The compelling demonstration is changing the supplier profile and watching the same project become relevant, unresolved, or unsuitable for transparent reasons.

## First paid version

Start as a service assisted by software. A founder reviews the evidence and prepares the briefs; the interface makes review and feedback consistent.

| Include in the pilot | Acceptance condition |
|---|---|
| One supplier segment and two proposed states | Customers confirm these boundaries match their actual market |
| Customer-approved capability profile | Every hard exclusion is visible and editable |
| A small curated project corpus | Every project has a durable identity and at least one accessible source |
| Evidence and fit worksheet | Every factual criterion is cited; unavailable facts show unknown |
| Project timeline and change digest | Repeated reports do not generate new-opportunity alerts |
| Save, assign, reject, and record outcome | Feedback is stored per customer with an audit trail |
| Weekly reviewed briefing and export | Includes only material updates and preserves source links |
| Source coverage indicator | Failed ingestion is visibly different from no new developments |

Defer automated outreach, contact scraping, bid submission, engineering design, a generic research chatbot, national coverage, predictive deal scores, mobile apps, and a broad CRM integration layer. A research action can be drafted for human use; sending messages or submitting bids is a separate future workflow.

## Data acquisition and evidence rules

The data problem comes before the interface. The current homepage scraping is useful for discovery but has too little industrial depth for the proposed product.

| Source class | Role | Initial access strategy | Limitation |
|---|---|---|---|
| Issuer releases and investor documents | Expansion, scope, milestone and contractor statements | Curated issuer list and manually added documents before automation | Published plans can change; private firms may disclose little |
| Government environmental proposal records | Project identity, location, disclosed scope and process status | Evaluate accessible PARIVESH records for the pilot corpus | Proposal or approval is not procurement intent |
| Public procurement notices | Explicit tenders, dates, requirements and awards | Link to original notices and test permitted access | Public tenders do not cover all private buying |
| Trade publications and current news feeds | Discover candidate developments | RSS, permitted metadata, or appropriate licensed access | Secondary reports need verification and may repeat old announcements |
| Customer-provided documents and subscriptions | Qualify opportunities already on a customer's radar | Authorized uploads or access consistent with the provider's terms | Customer access does not automatically permit bulk redistribution |

PARIVESH describes proposal tracking; the Government of India procurement portal offers tender search. These establish source categories worth investigating, not production-ready APIs, bulk access rights, or complete coverage. [PARIVESH](https://cpc.parivesh.nic.in/SingleWindow.aspx), [Government eProcurement search](https://www.eprocure.gov.in/eprocure/app?page=FrontEndAdvancedSearch&service=page).

In the first week, manually inspect at least 30 candidate records and build 10 complete project dossiers. Record how many have usable location, stage, scope, and stakeholder evidence, along with access method, refresh reliability, licensing constraints, and researcher time. If the public corpus cannot support qualification, test customer-supplied opportunities as an input before purchasing a data subscription or building connectors.

Preserve source URL, document hash, publication date when available, retrieval date, page or passage locator, source type, and permitted excerpt. Keep original statements separate from inferred relevance. Store documents only where rights permit; a public URL alone does not settle reuse rights. Do not bypass access controls or treat a blocked source as healthy.

Human review is mandatory for pilot-ready briefs. Exact citations support the facts extracted; they do not prove that a company intends to buy, that the supplier qualifies technically, or that a deal is available.

## Architecture and migration

Keep Flask and the current visual style for the pilot. A framework rewrite would not resolve the main uncertainty: whether customers value the qualification work.

The proposed pipeline is:

`Collect → preserve provenance → extract facts → resolve project identity → compare with prior evidence → match supplier profile → review → publish brief → record outcome`

Use persistent relational storage for history. SQLite is sufficient for a local concierge prototype; a shared paid pilot should use a managed database with tenant isolation and backups. Run collection and analysis in a separate scheduled worker, with run records, retries, timeouts, and idempotent processing. Web requests should read the latest successful published state.

Core records are Organization, Site, Project, SourceDocument, EvidenceClaim, ProjectEvent, SupplierProfile, Capability, FitAssessment, Review, and Outcome. Every assessment references the exact profile version, source versions, rule version, and model version that produced it. Scope, unit, and project phase belong to claims, not just free-text summaries.

| Existing file or behavior | Proposed treatment |
|---|---|
| `sources.py` | Retain the configuration pattern; add access method, document type, provenance and source health |
| Fetching in `mainFile.py` | Separate into source adapters; preserve snapshots and idempotent ingestion |
| `gemini_analyzer.py` | Reuse structured extraction and batching; replace stock sentiment with cited project facts and abstention |
| Headline-only cache key | Include source content, extraction schema, prompt and model versions |
| Intermediate CSV files | Retain as imports or exports; replace them as the authoritative shared state |
| `app.py` | Add project, supplier and review views; move refresh work outside the request |
| `templates/index.html` and `static/styles.css` | Reuse readable typography and themes; replace signal badges with qualification states |

Tenant isolation, authentication, guarded mutations, secret handling, job controls, auditability, and export/deletion behavior are required before private customer capability or sales information enters a shared pilot. Treat retrieved content as untrusted data: it must not control tools, rewrite rules, or authorize external actions.

For identity matching, use organization aliases plus site, project phase, identifiers, and dates. Similar company names alone must not merge projects. Route ambiguous matches for review. Extraction failures retain documents in a queue and never silently fall back to confident qualification labels.

## Pricing and business model hypotheses

Offer a **₹10,000 four-week paid pilot** for one team, one capability profile, the agreed territory, a weekly reviewed briefing, and up to 20 project qualification reviews across the pilot. A review can conclude no fit; do not promise a minimum volume of leads. Agree coverage and review capacity before charging.

Test **₹15,000 per month** after the pilot for three users and the same defined workload, with additional research scoped separately. Both prices are hypotheses to test through actual payment and renewal. No competitor price comparison or willingness-to-pay evidence supports them yet.

Illustrative monthly economics at ₹15,000 revenue:

| Direct cost assumption | Amount |
|---|---:|
| Six hours of review and support at ₹500 per hour | ₹3,000 |
| Allocated model and infrastructure costs | ₹750 |
| Allocated data acquisition or licensing | ₹1,500 |
| Total modeled direct cost | ₹5,250 |
| Contribution before acquisition, development, overhead, taxes and payment costs | ₹9,750, or 65% |

These are planning inputs, not vendor quotes. If review reaches twelve hours and data allocation reaches ₹4,000, direct cost becomes ₹10,750 and contribution falls to about 28%. Track labor honestly, including founder work. If that persists, narrow scope, raise price, partner for data, or stop; more automation is not automatically the answer.

Avoid a freemium feed at launch. A sample brief can show value without creating a large unpaid ingestion and support burden. Expand later through paid team workflows and specialized coverage, after renewal evidence.

## Validation and first customers

Recruit through relevant industry directories, supplier associations, existing professional contacts, and targeted founder outreach. These are proposed acquisition routes; this draft does not send messages or enrol anyone.

Interview ten relevant buyers. Ask them to walk through their last three pursued or rejected projects, show how they found them, identify what took time, and explain what information changed the decision. Establish existing tools and spend. Test willingness to pay with a concrete scoped pilot, not a general question about interest in AI.

For five interested teams, compare FieldSignal briefs against their existing process on the same projects. Capture which opportunities were already known, the time to reach a decision, errors, missing facts, and whether a new verification step was useful. Include rejected cases; a useful disqualification also saves work.

**Primary product metric:** customer-confirmed useful qualification decisions per active account per month. Count a decision only when the user records a reason and next step or rejection. Secondary metrics include review time, citation correctness, useful novelty, duplicate alerts, coverage failures, and renewal. RFQs are downstream evidence; they may take longer than a short pilot. Clicks and headline volume are not substitutes.

Proposed investment gates, not achieved targets:

| Gate | Evidence required | If it fails |
|---|---|---|
| Customer access | Ten relevant interviews within two weeks | Change to a reachable niche before rebuilding |
| Source feasibility | Ten reviewed dossiers from 30 candidates with useful scope and identity evidence | Test customer-provided inputs or a licensed partner |
| Paid demand | Three of five suitably qualified trial teams buy the scoped pilot | Revisit buyer, pain, and offer; do not add features to compensate |
| Practical usefulness | At least 70% of reviewed briefs judged useful for pursue, reject or investigate decisions | Tighten matching and evidence quality |
| Trust | All published factual claims cited; zero critical identity or procurement-status errors in the audited pilot sample | Pause publication of affected classes and repair the process |
| Continued value | At least two of the first three paid teams renew at the stated ongoing scope and price | Investigate novelty decay, workload fit, and economics |

Small samples guide the next investment; they do not prove a general market. Log all candidate projects and exclusions so the evaluation cannot hide poor coverage or cherry-pick good briefs.

## Delivery sequence

| Phase | Deliverable | Exit condition |
|---|---|---|
| Week 1 | Buyer interviews, source-access audit, three manual sample briefs | Evidence of a reachable buyer and usable source material |
| Week 2 | Ten dossiers, capability worksheet, pilot terms | Paid pilot commitments and agreed quality criteria |
| Weeks 3 and 4 | Persistent project history, profile matching, evidence review interface | The entire pilot workflow can be completed without manipulating CSV files |
| Weeks 5 and 6 | Operate four-week pilots as start dates allow; measure time, usefulness and errors | Documented customer decisions and reliable delivery |
| Weeks 7 and 8 | Renewal decisions and selective automation | Ongoing demand and an economically credible service |

This is a proposed sequence for a focused builder with part-time domain review. Customer access, document permissions, and data quality can extend it. Automate the tasks demonstrated to consume time; do not build a broad platform before those gates.

Longer term, expand to adjacent supplier categories only when the first category renews and its data economics work. A durable advantage could come from corrected project identities, versioned evidence, customer-approved capability models, and private feedback about fit. None exists as a moat today, and private customer data should not be pooled without explicit agreement.

## Code audit and verification appendix

The current homepage and source-filtered page return HTTP 200 in Flask's local test client. A negative page number clamps successfully. `/?page=abc` returns HTTP 500 because `int()` receives unvalidated input. All four Python source files parse successfully. These checks did not run the scraper, call a model, verify headline claims, or validate deployment.

Additional findings from the implementation:

1. The pipeline overwrites its CSV snapshots on each run. There are no publication or collection timestamps in the final row schema, so it cannot establish recency or compare changes.
2. The dashboard displays the current date and promotes the first row without timestamp sorting. Source order therefore influences prominence.
3. `/run_script` launches a synchronous subprocess. There is no explicit job status, run lock, authentication, or rate limit. Multiple requests can overlap shared-file writes; a failed subprocess is logged and followed by a redirect that can look successful to the browser.
4. Model classification and keyword fallback produce the same presentation. The fallback uses substring matching; neither method supplies article-body evidence. A structured JSON response constrains shape, not factual correctness.
5. The analysis cache is keyed by normalized headline only. It has no model/prompt version or expiry, so changed extraction rules do not necessarily replace prior results.
6. HTML extraction includes broad heading and list-item selectors. Filtering by word count does not distinguish an article from navigation or promotional copy.
7. `vercel.json` supplies routing but no persistent data architecture or background worker. Deployment suitability remains unverified; a shared service must not depend on durable writes to its application bundle.
8. No project test suite was found. Basic parsing and page-render checks do not test source failures, identity accuracy, citation quality, concurrent refreshes, or tenant boundaries.

The working tree already contained edits to the application, styles, data, and dependencies before this analysis. This proposal adds product documentation and a separate illustrative concept; it does not implement the pivot or alter the current application behavior.
