# Step 138 E through H — Leo integration and research closeout

Date: 2026-11-07 America/Los_Angeles. Workstream: unified integration,
security evaluation and research documentation.
Original research question, unchanged:
How do we create an MCP server integrated with Entra and an AI agent to help schedule classes for students at UNA?

## CONFIRMED phase disposition

| Phase | Observed result |
| --- | --- |
| A preflight | HEAD 748df1b verified, untracked evidence preserved, recovery archive saved, team pushes disabled, secure effective ports checked. |
| B restoration | RAGFlow v0.27.2 serving web and authenticated API; four dependencies healthy; n8n untouched. |
| C ingestion | Two separate private synthetic datasets created; six actual parsed, embedded and indexed documents each; nomic-embed-text through local Ollama. |
| D authorization | Real top-1 adversarial canary, five-role exact document matrix, metadata/content parity, refreshed-claim restrictions and foreign-tenant empty set passed. |
| E Leo | Explicit opt-in lab factory connected through existing AuthorizedKnowledgeRetriever and AuthorizedPolicyAnswerer; normal protected default remains disabled. |
| F tests | Final root 455 passed; agent 1073 passed/1 skipped; security subset 113 passed; Chromium smoke and two live RAGFlow five-turn trials passed. |
| G documentation | Master SOT and additive register updated; authorization report, this closeout and reproducible runbook added; historical archives untouched. |
| H GitHub | Library commit 0c04434906c5118d1168d2743dae4c85daba05b3 pushed only to origin integration branch; all 4 workflows/7 jobs succeeded. Final integration SHA is reported after commit. |

The library commit's CI details are preserved in
docs/evidence/2026-11-07-138-library-ci.json. The closeout commit's CI must
be observed separately; prior green jobs are not evidence for a later SHA.

## CONFIRMED live execution

scripts/leo_live_ollama_browser_probe.py now accepts an explicit trusted
manifest/credential pair. Neither browser JSON nor model arguments can select
the backend or supply ACLs. The existing scheduling runner's Policy: branch
still separates policy evidence from deterministic academic decisions.

Final trial used the independently reproduced corpus and reran the startup
canary before accepting a policy request. Model calls by turn: 3, 2, 2, 1, 0.
Mandatory Friday and Wednesday restrictions survived the two follow-ups;
the 10:01 soft start remained. CIS410 SEC2002 was proposed; CIS376 was
explicitly excluded by verified planner data. The policy answer displayed an
actual remote dataset/document/chunk source and the verified public excerpt.
The foreign-student request triggered the system privacy refusal without an
LLM call. Logout invalidated the session. No enrollment operation occurred.

Evidence:
- docs/evidence/2026-11-07-138-live-attempt1.json and matching PNGs.
- docs/evidence/2026-11-07-138-live-final.json and matching PNGs.
- docs/evidence/2026-11-07-138-browser.txt and its dedicated screenshot directory.
- docs/evidence/2026-11-07-138-root-closeout.txt and security-closeout.txt.
- docs/evidence/2026-11-07-138-agent.txt.

Desktop screenshots were visually inspected: original purple/gold Leo styling,
synthetic-data notice, partial exclusion and policy/privacy responses remain
readable. Automated smoke also checks mobile layout, identity mismatch, stale
context retry, logout and card rendering. Browser screenshots show a scrollable
conversation area, not the whole transcript at once.

Model: qwen3:4b-instruct, digest
0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0,
temperature 0, think false, num_ctx 8192, num_predict 512, timeout 150 seconds.
Embedding model: nomic-embed-text:latest, digest
0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f.
Container/service facts are recorded separately in the environment JSON.
No paid OpenAI generation service was used for these trials.

## CONFIRMED prompt and security boundaries

Existing captured-prompt regression
test_unauthorized_text_never_enters_model_and_policy_runner_is_read_only
injects an unauthorized Legal chunk and checks its text is absent from model
messages and output. The new
test_prompt_injection_in_authorized_document_cannot_expand_sources
places role-escalation/tool instructions inside an authorized document,
then simulates a model following them. The answerer exposes no tools, rejects
the unauthorized source/tool selection, returns no source and emits no cards.
These are controlled offline adversarial tests, not a universal guarantee about
every possible model output. Live trials independently verify authorized IDs.

Live server-role matrix uses synthetic trusted SecurityContext values. The
browser path separately verifies locally signed JWTs. Neither proves real
Microsoft Entra identity issuance or Graph directory revocation. Role/group
refresh tests use changed current claims. No test count here is model accuracy.

## CONFIRMED changes and checkpoints

Starting baseline: 748df1b7452339d6706a326ada81fc76ce6c2236.
Library phase: 0c04434906c5118d1168d2743dae4c85daba05b3.
Library files and detailed decisions are listed in
2026-11-07-step138-live-ragflow-authorization.md.
Integration adds scripts/leo_live_ollama_browser_probe.py flags and source checks,
tests/test_authorized_retrieval.py injection regression, sanitized screenshots,
JSON trial evidence, the runbook, and additive SOT records.
The initial 5 async-harness failures remain preserved and explained in the
library report. No application failures occurred in the two live browser trials.
Historical Phase 135F failed evidence remains untouched and untracked locally.

## Paper-ready findings and limitations

CONFIRMED — Architecture and method. This prototype separates signed identity
verification, read-only MCP academic access, deterministic scheduling, and
authorized policy retrieval behind a single Leo browser interface. A trusted
registry derives explicit document candidates from tenant/role/group ACLs.
The remote RAGFlow service ranks within that allowlist; returned chunks must
match authoritative local provenance, policy version/hash and content before
they reach policy source selection. The language model has no authority to
grant access, decide academic eligibility or perform enrollment.

CONFIRMED — Evaluation. We used six synthetic documents in a private
Elasticsearch-backed RAGFlow dataset, including a deliberately highly relevant
restricted decoy. With a one-candidate vector search, unrestricted retrieval
selected the decoy, while public-only and Student-only allowlists retrieved
their lower-scoring authorized records. The trial was repeated in a newly
ingested dataset. Five role identities each retrieved exactly their permitted
documents; claim-removal and group-overage cases excluded restricted content.
A real Chromium/HTTPS/Ollama run then integrated three scheduling turns, a
live policy retrieval, a privacy denial and logout. Automated tests separately
exercise forged metadata, content mutation, outages and prompt injection.

WORKING ASSUMPTION — Contribution. The combined design is a useful reproducible
case study of enforcing authorization outside an LLM while preserving
deterministic scheduling continuity. It supports a bounded engineering claim,
not an estimate of general security, retrieval quality or student outcomes.

OPEN QUESTION — External validity. The corpus is tiny, plain text and synthetic;
the registry is in memory; metadata is returned through document enrichment.
The observed canary does not inspect every backend execution path or prove
security for another vector engine, parser or deployment. Real Entra, Graph,
Banner, institutional documents and enrollment were not used. The team's
Haystack 11-test result, unified offline tests, live HTTP canaries and browser
trials are distinct evidence categories and must not be pooled.

RECOMMENDATION — Next work. Expand adversarial and multilingual corpora; capture
backend query-level traces under approved instrumentation; define durable ACL
synchronization and revocation freshness; obtain institutional role/data
approval before any deployment. Finish cross-workstream review and manuscript
claims using the preserved source hierarchy. Keep PR 3 draft.

## Reproduction and remaining decisions

Use docs/research/2026-11-07-step138-runbook.md for exact safe commands and
the demonstrated five-turn sequence. RAGFlow remains running locally; the demo
gateway stops after each automated trial. A persistent student-facing service
is not deployed. No user decision is required to rerun the current synthetic lab.
Real tenant/app role mappings, Graph access, real Banner and institutional
documents require the user's authorized owners and approvals.


## Publication verification and synthetic fallback regression

CONFIRMED on 2026-11-07: integration implementation commit
f5816fd69dca4cd23c0af88c7467912420facdc7 was pushed only to
origin/integration/browser-gateway-20261102. All 4 exact-SHA workflows and all
7 jobs passed, including Ubuntu/Windows Python 3.12/3.13, Chromium and two
WS1/WS2/WS3 integration runs. Evidence:
docs/evidence/2026-11-07-138-integration-ci.json.
The final documentation/evidence-only commit records this observed code checkpoint;
its own SHA and CI are reported after publication.

CONFIRMED: the original five-turn synthetic-retrieval mode also passed on this
implementation. It used local Ollama and Chromium, simulated signed Entra/Mock
Banner and the synthetic lexical backend, NOT RAGFlow. Evidence:
docs/evidence/2026-11-07-138-synthetic-regression.json and matching screenshots.
This is separate from the two successful actual RAGFlow browser trials.

CONFIRMED final service check: web HTTP 200; unauthenticated API HTTP 401;
authenticated API HTTP 200/code 0 with two preserved datasets. Dependencies
healthy, n8n unchanged. Evidence: docs/evidence/2026-11-07-138-service-final.json.
WORKING ASSUMPTION: service readiness persists only while this local lab runs.
OPEN QUESTION: production assurance remains outside these synthetic trials.
RECOMMENDATION: use the runbook and new evidence names for every repetition.
