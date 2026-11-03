> **DRAFT · 2026-11-01 America/Chicago** — source-linked synthesis; original records unchanged.

| Document control | Value |
| --- | --- |
| Status | CREATED / DRAFT; proposed for formal team review and adoption. Not a claim of finished integration. |
| Scope | Workstream 1 Mock Banner; Workstream 2 protected MCP; Workstream 3 AI agent/planning; Workstream 4 security/testing; separate personal experimental implementation. |
| Canonical source policy | Preserve originals unchanged. This document is the proposed consolidated index and narrative; no source is silently superseded. |
| As-of GitHub snapshot | Team repository main a55813c464… (PR #37 merged, GitHub timestamp 2026-11-02 UTC); personal main 4f3455d6f5…; personal research branch 7f5601b262…. |
| Classification | CONFIRMED; WORKING ASSUMPTION; OPEN QUESTION; RECOMMENDATION |

**Research-question preservation:** The original research question is reproduced verbatim on the next page. No change in research question is proposed or authorized.

_Not a journal manuscript, security certification, real-Banner integration, or team acceptance report. Private-source materials require a publication and privacy review before copying into any public repository._

# UNA MCP AI Scheduling Research — Master Source of Truth v1.0 (Draft)


## 1. Project identity, fixed research question, and scope

**Original research question — preserved exactly:**

“How do we create an MCP server integrated with Entra and an AI agent to help schedule classes for students at UNA?”

**CONFIRMED:** University of North Alabama Applied AI Systems Research Lab project. Objective: implement and evaluate an AI-assisted academic scheduling research prototype with MCP-mediated structured academic tools, a Microsoft Entra–oriented identity boundary, an AI conversational agent, and a synthetic Mock Banner service. The authorized final question wording remains unchanged.

**CONFIRMED architectural principle:** One student-facing conversational agent coordinates modular services. The language model handles conversation and tool selection. Deterministic application code—not the language model—judges prerequisites, corequisites, conflicts, course/section constraints, capacity, and credit limits. The structured academic-data authority is a synthetic Mock Banner service at present; a future approved Banner connection is not established.

**Status qualifier:** The team has demonstrated a synthetic WS3→WS2→WS1 authenticated MCP path. The private personal branch separately records synthetic browser and agent demonstrations. Real UNA Entra login, official student identity mapping, live Banner, persistent registration writes, and final RAG/OCR integration remain outside the verified integrated scope. [T2][T3][P2]

## 2. Evidence rules and document governance

| Label | Required interpretation |
| --- | --- |
| CONFIRMED | Grounded in inspected implementation, recorded source/commit, reproducible output, or faithfully attributed test observation; cite the source and revision. |
| WORKING ASSUMPTION | Design expectation not yet validated or approved; identify owner and verification needed. |
| OPEN QUESTION | Missing approval, missing evidence, unresolved interpretation, or a contradictory record. |
| RECOMMENDATION | Proposed future action or scientific experiment; never restate as implemented or successful. |

**Decision M-001 (CONFIRMED editorial direction, 2026-11-01 local):** Create one combined Master SOT from all four workstreams; use the private personal SOT as historical foundation; preserve William’s, Hassan’s, Bryson’s and personal original records. This does not authorize changes to the original research question. It does not imply technical decisions have been adopted by all teammates.

**Version policy:** v1.0 is a newly synthesized team-master draft, not a rename of personal v1.7. Each future phase should append a dated change entry with owner, exact source revision, test environment, expected/actual outcome, limitations, security implications, paper relevance and any decision state changes. Keep all original DOCX/Markdown records immutable.

**Evidence hierarchy:** Primary versioned code and raw run artifacts > CI/test transcript with configuration > named SOT/handoff summary > retrospective conversation summary > proposed implementation. Preserve conflicting claims with dates and explain when one is superseded by later evidence.

## 3. Source inventory and provenance

| Source ID | Original record | Version / status |
| --- | --- | --- |
| P1 | Personal SOT DOCX sequence, v0.x–v1.6 on personal main | v1.6 on main; personal historical backbone; original unchanged |
| P2 | Personal SOT v1.7 DOCX at private branch research/authenticated-mcp-integration-20261029 | Present at branch 7f5601b262; not merged into personal main; retain as branch checkpoint |
| P3 | Personal dated research notes: n8n tool accuracy, guard v4.x, Phase 7 browser, team WS2 addendum | Research evidence; some only on unmerged PR #3 |
| T1 | William: docs/mock-banner-sot.md | Team main after PR #37; original contribution record |
| T2 | WS2: docs/workstream2-mcp-integration.md | Team main after PR #29; authenticated synthetic integration record |
| T3 | Hassan: docs/workstream3-handoff.md, completion-summary.md, integration-contract.md | Team main; authored WS3 history and design/test contracts |
| T4 | Hassan: docs/evidence/2026-11-02-heldout2-report.md | Two-run frozen held-out model evaluation; separate pre-registered code revision |
| T5 | Bryson: docs/person4-source-of-truth.md | Team main after PR #36; security, testing, reproducibility |
| T6 | Team code, tests, README and docs/mock-data-model.md | Current sources of implementation facts; proposed data model must not override code |

**CONFIRMED current repo checkpoints at document creation:** Public team repository main: a55813c464ac3b4587a935b63aae444219651222 (includes PRs #29, #34–#37). Private personal main: 4f3455d6f5…; research branch: 7f5601b262… (includes v1.7 document). GitHub UTC timestamps may display November 2 for local Central Time work performed late November 1.

**OPEN QUESTION / audit gate:** The personal v1.7 DOCX was located and its Git blob existence/branch SHA verified, but the Word binary has not been fully extracted and line-reconciled in this consolidation session. The paper-grade final master must check every v1.7 section against this synthesis before team adoption. Related Markdown phase addenda and the v1.6 history were reviewed as supplemental sources. [P2][P3]

## 4. Workstream contributions and non-overlapping responsibilities

| Workstream | Attributed scope | Evidence and remaining scope |
| --- | --- | --- |
| WS1 — William | Mock Banner FastAPI; student/course/section/history/enrollment/term read-only GET routes; final API test expansion; implementation and handoff. | 13 routes; 28 API tests passed in dated component runs; no live Banner, persistence or API-native auth. Initial baseline API tests credited separately to Bryson. [T1] |
| WS2 — personal MCP / team integration owner | Protected MCP service, token/identity checks, typed tool adapter, WS3→WS2→WS1 signed-synthetic integration and associated CI/research artifacts. | Team PR #29 merged; 6 read-only MCP tools; synthetic per-student denial. Real Entra access and university mapping not proven. [T2][P3] |
| WS3 — Hassan | SchedulingAssistant, MCP client, typed academic models, planner, preferences, grounding, anti-leak safeguards, evaluation datasets and handoff. | Scripted/offline and live-model evidence must be separate; known tool/answer failures remain. [T3][T4] |
| WS4 — Bryson Black | Independent API regressions, synthetic JWT verification/authorization checks, environment/testing documentation, security-readiness SOT. | Root suite documented as 67 passing in a later historical run; no real Microsoft Entra tenant/JWKS integration assurance. [T5] |
| Personal experimental full-build | Extended deterministic scheduling, 8-tool development MCP, RAGFlow adapter, n8n evaluations, answer guards, synthetic browser gateway and multi-service agent. | Separate personal repository and draft branch; not all pieces merged or tested together with current team main. [P1][P2][P3] |

**Attribution safeguard:** Initial team dataset authorship is not automatically assigned to William: his SOT notes that early design/data commits used the generic “MCP Server” author label. Bryson authored the original API testing baseline; William expanded tests and implemented API functionality. Avoid equating PR ownership with authorship of unrelated components. [T1]

## 5. Confirmed architecture and trust boundaries

```text
Student chat / session interface (personal synthetic browser candidate)
    -> authenticated server-side user/session context (not LLM-provided)
    -> one AI orchestration agent
         | -> typed read-only MCP scheduling tools
         |      -> independent per-student authorization
         |      -> deterministic course/schedule planner and validator
         |      -> synthetic Mock Banner academic records (WS1)
         | -> policy/knowledge retrieval adapter (RAGFlow candidate)
                <- OCR-based knowledge ingestion (planned, not integrated)
```

**CONFIRMED team integration:** Team WS3 SchedulingAssistant→BannerTools→WS2 protected Streamable HTTP MCP→WS1 FastAPI/JSON with six read-only tools. The WS2 backend adapter currently uses in-process ASGITransport to the existing FastAPI app. Signed synthetic JWTs and synthetic student mappings were used in offline tests. The protected service is loopback-bound and fail-closed without Entra configuration. PR #29 was subsequently merged into team main. [T2][T3]

**CONFIRMED personal branch experiment:** A separate opt-in Playwright/Chromium test drove committed student chat JavaScript through an actual FastAPI session gateway, live local Ollama agent, protected MCP ASGI and protected synthetic Banner application, plus synthetic policy retrieval. It was a single recorded in-process test with locally signed simulated identity. It did not demonstrate a deployed browser over real HTTPS or a real Entra login. [P3]

**RECOMMENDATION:** A final integrated application should have one canonical student-context authority, one server-side authenticated MCP client boundary, one authoritative academic validation engine, and separate RAG/OCR knowledge responsibilities. Keep interfaces replaceable and treat model output as untrusted. Do not copy both validators into production without an explicit ownership/reconciliation decision.

## 6. Chronological project and decision history

| Date / period | Milestone | Evidence / limitation |
| --- | --- | --- |
| 2026-09-28 | Original MCP + Entra + AI scheduling research direction; Mock Banner and OpenAPI development arrangement. | Personal SOT history; research question unchanged. [P1] |
| 2026-10-05 to 10-06 | Personal synthetic fixtures, deterministic prerequisite/conflict/capacity/credit logic, Mock Banner API, MCP MVP, OpenAPI contract. | Personal SOT records milestones and regressions; do not treat historical test counts as current combined-suite results. [P1] |
| 2026-10-17 to 10-22 | WS3 planner/agent, preferences, security/evidence checks, evaluations, CI, handoff; core team work underway. | Numerous merged PRs; original evaluations tied to historical code revisions. [T3] |
| 2026-10-18 to 10-26 | William builds Mock Banner endpoints via PRs #15–#18, #20–#22; Bryson adds initial API suite via PR #19. | 28/28 historical API tests, one non-failing deprecation warning; component-only scope. [T1][T5] |
| 2026-10-26 to 10-28 | Personal n8n repeated tool-selection experiment; 18-row scheduling study; progressive answer-quality guard experiments. | Fixed test prompts, synthetic dev MCP; tool accuracy distinct from final-answer correctness. [P3] |
| 2026-10-29 | Personal synthetic identity/browser gateway research branch, guarded agent, RAG adapter, and opt-in full-chain Chromium/Ollama/MCP test. | One 18.898 s recorded full-path conversation; in-process/simulated auth; branch is not personal main. [P2][P3] |
| 2026-10-29 to 11-01 local | Team WS2 integrates protected MCP with WS3 agent and WS1 Mock Banner. | PR #29; synthetic HTTP tests and local live Ollama demo, not university identity integration. [T2] |
| 2026-11-01 local | WS3 additional regression/security work, team synthesis and heldout2 run execution. | 1036 passed + 1 skipped WS3 baseline; separate root suite 53; heldout2 evaluated frozen earlier code. [T3][T4] |
| 2026-11-01 local / 11-02 UTC | Team merges Bryson SOT PR #36 and William SOT PR #37, and heldout2 report PR #35. | Current team main a55813c…; current master document newly drafted. [T1][T4][T5] |

## 7. Verified functionality by boundary

| Area | CONFIRMED current observation | OPEN limitation |
| --- | --- | --- |
| Academic API | WS1 13 read-only routes for synthetic entities; filters and missing records; 28 API tests in its recorded component run. | No real Banner, API-native authorization, enrollment writes, or production contract guarantee. [T1] |
| MCP tools | WS2 6 read-only tools compatible with team WS3; structured error codes; authenticated synthetic tests. | Not the same tool surface as the personal 8-tool development server; production Entra unresolved. [T2] |
| Academic validation | WS3 deterministic rules and preference/ranking logic; personal engine independently implements generation/validation. | One canonical academic rule engine and course/coreq semantics need integration decision. [T3][P1] |
| Agent interaction | Team agent has a tested tool-calling/guarded loop; private branch has unified agent/RAG and student-facing browser experiment. | No single current team-main deployment integrates all personal capabilities. [T3][P3] |
| Identity | Synthetic JWT verification and per-student access refusal, including before unauthorized backend reads. | No university-approved Entra tenant, account-to-student mapping, real JWKS deployment or production cookies. [T2][T5] |
| Knowledge services | Personal RAGFlow retrieval adapter with synthetic/mock tests and synthetic policy-retrieval use in a browser-chain test. | No verified live RAGFlow+team-main full system; OCR ingestion remains integration work. [P3] |
| Repeatability | Automated tests, frozen datasets, CI and scriptable local commands exist. | Results reflect different revisions, datasets and test modes; controlled integrated benchmark not yet run. [T3][T4][P3] |

## 8. Evidence ledger: separate denominators and test modes

**Rule:** Do not add pass counts from unrelated suites or calculate one “overall accuracy.” Each observation has its own revision, dataset, environment and meaning. Earlier outcomes are retained, not silently upgraded.

| Evidence ID | Recorded observed result | Interpretation / caveat |
| --- | --- | --- |
| E-WS1-01 | William API: 28 passed, 1 warning; a fresh rerun at team baseline 220e325 reported 28 passed in 0.75 s. | Tests retrieval behavior with TestClient; not MCP auth or academic schedule correctness. [T1] |
| E-WS4-01 | Bryson root API/MCP/security suite: 67 passed, 0 failed (historical local result); Entra JWT verifier targeted tests: 14 passed. | Synthetic tests and local public-key substitutions; not live Entra verification. Earlier and later root counts must not be added. [T5] |
| E-WS3-01 | WS3 offline at 052336f: 1036 passed, 1 skipped; root suite at that checkpoint: 53 passed. | Uses scripted model and test oracles; not a real-model success rate; separate from later root 67. [T3] |
| E-WS2-01 | Team PR #29: signed JWT HTTP path through actual WS3 assistant + planner + WS2 + WS1 passed scripted integration; root 53 and WS3 874 passed + 1 skipped at earlier integration baseline. | True synthetic integration; model calls scripted for the automated case. [T2][P3] |
| E-WS2-02 | Team demo: qwen3:4b-instruct 39.09 s; una-scheduler:latest 52.89 s for one local scheduling conversation each; cross-student denial observed with zero academic MCP calls. | Exploratory, model- and machine-specific local runs; do not generalize latency/accuracy. [T2] |
| E-PER-01 | Personal n8n: four fixed prompts repeated five times; first tool + specified arguments matched 20/20 recorded attempts. | Only four distinct prompts; 3 course-retrieval tools; development MCP; not novel held-out accuracy. [P3] |
| E-PER-02 | Personal n8n Round 02: 16/16 predefined tool + required-argument PASS; two exploratory questions NOT_SCORED. | Incorrect yes/no polarity and overconfident “assigned/available” language remained; tool accuracy ≠ answer correctness. [P3] |
| E-PER-03 | Personal synthetic browser chain: one live Ollama + protected MCP + Mock Banner + synthetic policy result passed; measured conversation 18.898075 s. | One opt-in Playwright-in-process run at 67df1a1; not real Entra/HTTPS deployment or performance benchmark. [P3] |
| E-WS3-02 | First held-out WS3: 25/34 in two runs on historical code. | Subsequent fixes used failures, so set later became development data. [T3] |
| E-WS3-03 | Second heldout2: 23/37 (62.2%) in each of two CPU runs, 37/37 runtime grounded, one false academic claim per run. | Original pre-registered code d4eacbf, not modern team main; 35/37 identical pass/fail; dataset author not blind. [T4] |

## 9. Research-relevant observations and interpretation

### 9.1 Tool invocation and final-answer quality are different targets

**CONFIRMED:** In the personal n8n Round 02 experiment, the 16 scored cases met tool/argument criteria while some final answers used misleading language about course completion or implied registration eligibility/assignment. In the team heldout2 evaluation, all 37 responses passed the runtime grounding check in each run yet one false academic claim occurred per run. These are related but **not directly pooled** findings because the systems, models, measures and datasets differ. [P3][T4]

**RECOMMENDATION:** For integrated evaluation, measure (a) first tool/arguments, (b) complete tool sequence, (c) academically valid final proposal, (d) factual answer claims, (e) whether “proposed” is distinguished from “registered,” and (f) response latency as separate endpoints.

### 9.2 Identity enforcement should be outside the LLM

**CONFIRMED:** The team protected MCP path rejects cross-student synthetic access using authenticated context, and the personal browser branch reports synthetic cross-student denial before model execution. **LIMITATION:** Neither establishes deployment with actual UNA delegated access tokens. [T2][T5][P3]

### 9.3 Agent safety and usability can conflict

**CONFIRMED:** The heldout2 security analysis reports 10/11 attack cases passing in each run; legitimate queries worded similarly to attacks passed 2/3 and 1/3. This motivates measuring false-positive refusals, not just blocked attacks. [T4]

### 9.4 Reproducibility is a contribution; it is not generalization

**CONFIRMED:** Team frozen datasets, source revisions, CI and two heldout2 executions make failure analysis stronger than a one-off demonstration. However only one model, CPU runs, two repetitions and developer-authored datasets limit population-level claims. Model temperature 0 did not yield identical wording (only 6/37 identical final texts). [T4]

## 10. Integration design recommendations (not executed in this document)

| Decision ID | RECOMMENDATION / acceptance gate | State |
| --- | --- | --- |
| I-001 | Establish new integration repository preserving Git provenance and original evidence; define a canonical dependency lock and CI strategy. | RECOMMENDATION; repository not created |
| I-002 | Adopt WS1 API with validated schemas; retain William’s endpoint behavior and tests, and reconcile personal OpenAPI/typed models. | RECOMMENDATION; contract diff/test needed |
| I-003 | Choose one authorized MCP server entrypoint; map six team tool names vs personal eight tool surface via explicit adapter contract. | OPEN design selection |
| I-004 | Keep student/session identity server-bound and checked at MCP; prevent unprotected direct Mock Banner data exposure. | RECOMMENDATION; real Entra remains OPEN |
| I-005 | Define a single authoritative deterministic academic validation engine and one rule/fixture policy; preserve independent tests. | OPEN technical adjudication |
| I-006 | Integrate team preference/grounding mechanisms with personal agent/RAG; decide whether n8n stays evaluation-only or runtime. | OPEN integration choice |
| I-007 | Connect approved RAGFlow datasets and OCR ingestion only when evidence and privacy policies are recorded. | OPEN; no team full-chain proof |
| I-008 | Implement student chat UX with safe session handling, explicit “proposed only” answers, and no unsupported enrollment promise. | RECOMMENDATION; personal synthetic candidate |
| I-009 | Run complete CI, synthetic end-to-end and new frozen live-model benchmark before changing readiness claims. | RECOMMENDATION; tests not run here |

## 11. Proposed research-paper evidence strategy

**Research question remains unchanged.** A plausible paper contribution is a measured, identity-aware MCP academic scheduling architecture, not the generic claim that no prior course-scheduling assistant exists. Do not claim publication novelty or acceptance before a related-work comparison.

| Study | Comparison / controls | Primary metrics |
| --- | --- | --- |
| Architecture / interoperability | Same student/course fixtures and agent prompts; compare direct service adapter vs MCP with identical authorization policy where possible. | Interface changes required, contract compatibility, error handling, overhead/latency. |
| Academic safety | Same cases and LLM; vary authoritative deterministic validation or guard layer in a controlled sandbox (never permit unsafe writes). | Invalid proposals emitted, false eligibility/registration claims, correct rule explanations. |
| Security / identity | Synthetic distinct students, forged IDs, absent/expired/invalid-scope tokens, malformed backend data. | Unauthorized access denied before backend, allowed access success, false-positive refusals, safe error leakage. |
| Model / agent performance | Freeze a new unseen prompt suite after integrated implementation; same data, rules and scorer for each model/configuration. | End-to-end task success, correct tool paths, student-facing claim accuracy, constraint satisfaction, latency/tokens. |
| Retrieval grounding (optional) | Same policy questions with/without validated RAG retrieval; approved synthetic/public documents only. | Answer correctness, evidence citations, unsupported claims, retrieval miss/failure handling. |

**OPEN QUESTION:** Confirm target venue, formatting and ethical/data requirements with the professor before determining final experimental scope. Keep the original research question; these are supporting subexperiments, not rewritten objectives.

**Risk of contamination:** The team’s heldout2 37-case benchmark is valuable historical test evidence; after its failure report informs future fixes, it is no longer a fresh independent post-integration test. Use a new blinded/held-out set with a frozen scoring rubric and document any deviations. [T4]

## 12. Current open questions / risks (prioritized)

| Priority | OPEN QUESTION | Owner / verification trigger |
| --- | --- | --- |
| P0 | Approved Microsoft Entra tenant/app registration, scopes, real delegated JWT verification and trusted `(tid, oid)`→student mapping? | University/professor + WS2/WS4; no real students until approval. |
| P0 | Can the direct Mock Banner API be reached outside MCP and bypass student-level authorization? | WS1/WS2/WS4 threat model + network/security tests. |
| P0 | Which scheduling validator is authoritative and what prerequisite/corequisite/minimum-grade policies are supported? | WS1/WS3/WS2 agreement + oracle test fixtures. |
| P1 | Will WS3 agent retain the same behavior against the final tool names/shapes, student session, timeout and errors? | Integration contract tests + signed synthetic HTTP tests. |
| P1 | Does the unified browser/agent/MCP/RAG path work across multiple students, concurrent sessions, repeated runs and failure injection? | New integrated E2E and load/isolation tests. |
| P1 | What is the exact status of live RAGFlow, OCR document intake, document approvals and source citations? | RAG/OCR owners + reproducible smoke/quality tests. |
| P1 | Are private personal SOT and experiment logs safe and authorized to publish? | Project team/professor publication review; sanitized export. |
| P2 | What results can support a well-controlled comparative research study before paper submission? | Team + professor: preregister methods and choose fresh dataset. |
| P2 | Have all personal v1.7 DOCX sections and team historical notes been fully reconciled? | SOT curator: source-by-source audit and signed status update. |

## 13. Next-phase execution and documentation protocol

1. Review this draft with William, Hassan, Bryson and the WS2 coordinator; resolve ownership and missing evidence. Do not overwrite original SOTs.
1. Reconcile personal DOCX v1.7 and private branch addenda section by section; flag discrepancies rather than selecting whichever sounds best.
1. Freeze current public team and private branch commit SHAs and identify the new integration repository after privacy/access review.
1. Create an integration contract covering identity, tool names, arguments, response envelopes, academic error codes and authoritative validation ownership.
1. Implement incrementally with feature branches and reviewed PRs; each merged phase produces unit/contract/E2E results, a negative-security run and a new append-only Master SOT entry.
1. Design and freeze a new post-integration evaluation dataset, model/run configuration and human answer-quality rubric before observing outputs.
1. Draft paper sections directly from source-linked evidence; qualify negative results and synthetic-only external validity. Obtain professor/team approval for submission and publication.
## 14. Append-only decision and change register

| Entry | Type | Record / outcome |
| --- | --- | --- |
| M-001 / 2026-11-01 local | CONFIRMED editorial choice | User selected Option A: combined Master SOT drawing from all four workstreams and preserving originals. |
| M-002 / 2026-11-01 local | CONFIRMED scope constraint | Original project research question preserved verbatim; no scientific scope change authorized. |
| M-003 / 2026-11-01 local | CONFIRMED artifact action | Created new combined SOT v1.0 draft as an independent artifact; no repository writes, integrations or new tests. |
| M-004 / review pending | OPEN QUESTION | Confirm formal team adoption, canonical repository destination, public/private storage rules, and editor/change approvals. |
| M-005 / integration pending | RECOMMENDATION | Use new project repository and evidence-driven integration gates; do not claim project integration finished now. |

**Required next update format:** Date/time (timezone) | workstream owner | source revision/branch/PR | objective | files changed | commands/procedure | expected vs observed results | errors/fixes | security/privacy effects | reproducibility | evidence ID | CONFIRMED / ASSUMPTION / OPEN / RECOMMENDATION | resulting paper insight | next action.

## 15. Source reference index / archival links

[P1] Personal main repo SOT v1.6: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/main/docs/UNA_MCP_Source_of_Truth_v1.6.docx
[P2] Personal research branch SOT v1.7: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/research/authenticated-mcp-integration-20261029/docs/UNA_MCP_Source_of_Truth_v1.7.docx
[P3] Personal Phase 7 checkpoint and team WS2 addendum: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/research/authenticated-mcp-integration-20261029/docs/research/UNA_MCP_SOT_Phase7_Completion_Checkpoint_2026-10-29.md
[P3a] Personal team WS2 addendum: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/research/authenticated-mcp-integration-20261029/docs/research/2026-10-31-SOT-phase-addendum-team-WS1-WS2-WS3-integration.md
[P3b] Personal Round 02 study: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/main/docs/research/2026-10-28-n8n-scheduling-evaluation-round-02-complete-results.md
[P3c] Personal five-round repeatability: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/main/docs/research/2026-10-27-n8n-mcp-five-round-repeatability-results.md
[P3d] Personal live synthetic browser full chain: https://github.com/cadomyetz79/una-mcp-scheduler-personal/blob/research/authenticated-mcp-integration-20261029/docs/research/2026-10-29-phase7-step32-live-chromium-ollama-protected-mcp-banner-passed.md
[T1] William Mock Banner SOT: https://github.com/cadomyetz79/una-mcp-scheduler/blob/main/docs/mock-banner-sot.md
[T2] Team protected MCP integration: https://github.com/cadomyetz79/una-mcp-scheduler/blob/main/docs/workstream2-mcp-integration.md
[T3] Hassan WS3 handoff and summary: https://github.com/cadomyetz79/una-mcp-scheduler/blob/main/docs/workstream3-handoff.md
[T3a] WS3 completion summary: https://github.com/cadomyetz79/una-mcp-scheduler/blob/main/docs/workstream3-completion-summary.md
[T4] Heldout2 end-to-end eval (37 cases, two runs): https://github.com/cadomyetz79/una-mcp-scheduler/blob/main/docs/evidence/2026-11-02-heldout2-report.md
[T5] Bryson Person 4 SOT: https://github.com/cadomyetz79/una-mcp-scheduler/blob/main/docs/person4-source-of-truth.md
[T6] Team current repository: https://github.com/cadomyetz79/una-mcp-scheduler
[PR29] Team protected MCP merged integration: https://github.com/cadomyetz79/una-mcp-scheduler/pull/29
[PR37] William SOT merged PR: https://github.com/cadomyetz79/una-mcp-scheduler/pull/37
**Archive instruction:** Store the unmodified originals and raw private experiment artifacts in their current repositories or a restricted evidence archive. The combined SOT should link to them rather than duplicating sensitive content into the public team repository. Freeze any future publication copy against a reviewed commit/manifest.