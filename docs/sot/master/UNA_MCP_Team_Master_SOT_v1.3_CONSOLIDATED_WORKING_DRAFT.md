# UNA MCP AI Scheduling Research Project
## Master Source of Truth — v1.3 Consolidated Working Draft

**Current scope notice (2026-11-11):** The team selected **Haystack** as the RAG workstream for the research-paper scope; real UNA Banner and Entra access will not be used. The verified integrated Leo browser checkpoint (fb15003) still uses **RAGFlow**, not Haystack. The last inspected separate Haystack snapshot is archival evidence (7ef1b01); the linked team's GitHub repository is currently inaccessible to the connected account (404). The Haystack-to-Leo integration and latest team tests remain **UNVERIFIED**. Read the new Step 145 phase addendum before interpreting historical “current” statements. All earlier work is preserved as dated historical evidence.

**Latest dated update (2026-11-07):** Step 138 live synthetic RAGFlow and Leo
implementation f5816fd69dca4cd23c0af88c7467912420facdc7, exact-SHA CI verified.
See the appended Step 138 records and research closeout for current findings.
The original consolidation snapshot below is retained as historical context.

**Consolidation date:** November 4, 2026 (America/Chicago)  
**Original November 4 integration checkpoint:** `29e031554a20baf05cbb46fe351713eba5c2a03e` (`integration/browser-gateway-20261102`)
**Repository:** `cadomyetz79/una-mcp-unified-scheduler`  
**PR:** [#3, authenticated Leo browser gateway and verified schedule cards](https://github.com/cadomyetz79/una-mcp-unified-scheduler/pull/3) — **OPEN / DRAFT**  
**Document status:** **WORKING DRAFT; not signed off or formally adopted by all four workstreams.**

> **Preservation note.** This v1.3 is a synthesized current-status Master SOT and evidence reconciliation, **not** an in-place overwrite or byte-for-byte reflow of the historical v1.2 full-source Word draft. The full v1.2 DOCX and all historical originals remain canonical archival inputs. Its source-by-source factual and visual reconciliation is **OPEN**. This document references them explicitly and should be incorporated into the full-source Master SOT after team review; never discard original text, source IDs or version history.

---

## 1. Immutable research question, objectives and boundaries

**Original research question, preserved verbatim:**

> “How do we create an MCP server integrated with Entra and an AI agent to help schedule classes for students at UNA?”

**CONFIRMED — project objective.** A secure, testable, reproducible *research prototype* of an AI-assisted student scheduler for the University of North Alabama. The student interacts with one conversational assistant (Leo) while the AI agent orchestrates specialized backend services. MCP exposes structured academic tools; a deterministic planner makes academic eligibility and schedule-validity decisions; a Mock Banner HTTP API supplies synthetic academic records. An Entra-oriented authorization design is implemented and tested with **synthetic signed JWTs and simulated OAuth approval**, not university-approved live accounts.

**CONFIRMED — design constraint.** The language model must not be authoritative for prerequisites, corequisites, meeting conflicts, capacity, credit limits, student identity, registration state, or authorization. Verified schedule cards are *proposals only*. No code or test result should be described as completing actual student enrollment.

**CONFIRMED — additional modular design direction.** Optional public-policy RAG and student-bound synthetic OCR evidence-handoff contracts are separate from authoritative Banner records. OCR is ingestion/preprocessing and cannot substitute for verified academic history. The currently verified Leo browser integration does **not** demonstrate an operational university RAGFlow corpus or live OCR document processing.

**OUT OF VERIFIED SCOPE.** Real Microsoft Entra tenant, real delegated student login, actual UNA Banner API access, real student data, official deployment, FERPA approval, student registration writes, production-appropriate distributed sessions, and production-grade reliability.

## 2. Governance, classification and source hierarchy

| Classification | Required standard |
| --- | --- |
| **CONFIRMED** | Directly traceable to inspected versioned code, recorded tests, source file or observed and attributed run; retain exact commit, environment and denominator. |
| **WORKING ASSUMPTION** | Plausible design or experimental choice; owner and validation step still required. |
| **OPEN QUESTION** | Incomplete evidence, scope decision, requirement, institutional approval, or unresolved contradiction. |
| **RECOMMENDATION** | Proposed future action, not a claim that work has happened. |

**Source hierarchy:** versioned code and raw run artifacts > dated CI/test evidence at a fixed SHA > named technical SOT / handoff report > retrospective summaries > proposed work. Different test suites and benchmark generations must never be pooled or called one overall accuracy score. An earlier finding stays in the record when a subsequent code fix addresses it.

**Governance:** Do not push directly to original team `main` or `team-upstream`; keep the unified research feature branch and draft PR until reviewed. Do not treat a green CI check as official institutional approval. Where personal and team records disagree, cite both with dates and assign a reconciliation owner. Do not expose secrets, raw identity records, student transcripts or private data in public research artifacts.

## 3. Source inventory and author attribution

| Source identifier | Owner / scope | Preserved primary source |
| --- | --- | --- |
| **S-ARCH** | Full historical master compilation | `docs/sot/master/UNA_MCP_Team_Master_SOT_v1.2_FULL_SOURCE_CONSOLIDATION_DRAFT.docx` (unmodified archive) |
| **S-INV** | Source integrity / inventory | `docs/sot/master/SOURCE_INVENTORY_AND_VALIDATION.json` |
| **S-TEAM-v1** | Prior source-linked team synthesis | `docs/sot/source-history/UNA_MCP_Team_Master_Source_of_Truth_v1.0_DRAFT.md` |
| **S-PER-v1.7** | Personal technical/research history | `docs/sot/source-history/UNA_MCP_Source_of_Truth_v1.7.docx` |
| **S-REGISTER** | Additive integration decision chronology | `docs/sot/reconciliation/2026-11-02-unified-implementation-decision-register.md` |
| **S-WS1** | William — Mock Banner backend | `docs/mock-banner-sot.md` |
| **S-WS2** | WS2 MCP / identity / integration coordinator | `docs/workstream2-mcp-integration.md` |
| **S-WS3** | Hassan — agent / deterministic planner / evaluation | `docs/workstream3-handoff.md`, `docs/workstream3-completion-summary.md`, `docs/workstream3-integration-contract.md`, `docs/workstream3-integration-audit.md` |
| **S-WS4** | Bryson Black — security, API testing and reproducibility | `docs/person4-source-of-truth.md` |
| **S-STEP133** | Integrated Leo weekday-continuity phase | `docs/research/2026-11-04-leo-weekday-continuity.md` and linked evidence |
| **S-STEP134** | Integrated Leo concurrency phase | `docs/research/2026-11-04-leo-context-concurrency.md` and linked evidence |

**CONFIRMED from the historical synthesis:** William developed the WS1 Mock Banner routes and expanded API tests; Bryson provided the original API testing baseline. Hassan developed the WS3 scheduling agent/planner/evaluation infrastructure. The protected team WS2 MCP interface was integrated with student-bound synthetic authorization. The separate personal research work produced earlier agent/browser/RAG/OCR prototypes later selectively adapted. Individual commits must be consulted before assigning precise authorship of a particular code line or test case.

**OPEN:** The v1.2 full-source document was preserved in the unified repo, but complete paragraph-by-paragraph review against the v1.7 personal SOT and all four teammates' original records, visual QA, and team acceptance remain unfinished. A historical register asserts 803 personal paragraphs, 19 personal tables, 241 v1.0 Markdown lines and 4,100 Word paragraphs in v1.2; those inventory numbers were **not revalidated in this document-generation session** and must not substitute for an audit.

## 4. Current confirmed architecture and trust boundaries

```text
Student → Leo interactive browser (synthetic research interface)
   → HTTPS FastAPI gateway: exact origin + CSRF + opaque server-side cookie
   → simulated Entra OAuth state/PKCE + locally signed synthetic JWT
   → verified student mapping / active session and bounded PlanContext
   → authenticated AI agent (Ollama qwen3:4b-instruct in local trials)
       → team WS2 protected read-only MCP (6 tools)
            → team WS1 Mock Banner FastAPI/JSON synthetic academic API
       → team WS3 deterministic planner, constraints and evidence guards
       → optional read-only RAGFlow/public-policy retrieval adapter [contract tested]
       → optional student-bound synthetic OCR evidence validator [contract tested]
   → verified proposed-only cards / explicit refusal or partial explanation
   → session context revision control; logout revocation
```

**CONFIRMED:** The integrated browser/model/MCP demo uses real local Chromium-to-loopback HTTPS requests, a simulated offline identity-provider approval, locally verified synthetic JWT and protected MCP through an in-process ASGI transport. Therefore it establishes a *synthetic local end-to-end execution*, **not** a production network-separated or official Entra + Banner deployment.

**CONFIRMED academic decision ownership:** The protected tools authorize data access; the deterministic WS3 planner validates course/section choices, prerequisites, capacity, conflicts, registration-fit and academic constraints. The agent may select tools or format prose but may not invent course status, register students, or override verified planner output. Per-student authorization occurs outside the LLM. Existing registrations may be represented as checked facts and compatibility indicators; no write occurs.

**CONFIRMED browser state:** Server-bound `PlanContext` is constructed from verified planner evidence rather than model prose. Narrow follow-ups can reconstitute a request from trusted context; unsupported follow-ups are not silently merged. Continuity checks prevent previously required restrictions being lost. Step 134 introduced a session-only optimistic revision counter and atomic finalization: stale overlapping results return HTTP 409 and revoked/expired sessions return HTTP 401 at finalization. The in-process lock is not a multi-worker production store.

**CONFIRMED modular knowledge status:** The six personal RAGFlow/public-policy and synthetic OCR contract/test files were imported and compared; focused tests passed (38 in Step 37) without changing the team planner or six-tool MCP contract. The imported OCR validator is *not* an OCR engine. Real RAGFlow retrieval from an approved dataset and actual scanned-document ingestion through the final Leo application are **OPEN**. Never describe those imports alone as completed integration.

## 5. Chronology and important implementation decisions

| Period / checkpoint | CONFIRMED work | Evidence caveat |
| --- | --- | --- |
| 2026-09-28 through October | Research scope, mock Banner, protected MCP, deterministic scheduling, Entra simulation plan, personal RAG/OCR prototypes, and team workstream implementations. | Historical source and test revisions differ; preserve originals. |
| 2026-10-17 through November 1 | WS1 Mock Banner API; WS2 authenticated six-tool MCP; WS3 agent/planner + evaluation; WS4 independent security tests and SOT. | Component and synthetic integration evidence; not production deployment. |
| 2026-11-01/02 | Team Master SOT v1.0 and v1.2 full-source draft assembled; unified repository and protected source-history strategy established. | Master v1.2 factual and visual reconciliation still open. |
| 2026-11-02 | Read-only RAGFlow adapter and OCR evidence contracts imported into unified codebase with focused offline tests. | Contracts imported; no live RAGFlow/OCR final end-to-end proof. |
| 2026-11-02/03 | Leo frontend, OAuth/PKCE synthetic callback, token/session/CSRF/origin checks, protected MCP and plan cards, Chromium UI, live Ollama proof. | Browser→HTTPS loopback; MCP ASGI in-process; simulated identity. |
| Steps 120–126, Nov 3 | Verified two-turn start-time reconstruction; discovered and fixed omitted soft preference strength in deterministic model-argument reconciliation. | Offline regressions and later live comparison, not arbitrary conversational memory. |
| Steps 127–130, Nov 4 | Live two-turn success recorded; three independent repeats passed with same prompts, 3/3 success. | One narrow scenario, descriptive 100% only; not production reliability. |
| Steps 131–132, Nov 4 | Five follow-up scenarios exposed loss of mandatory Friday on a Wednesday addition; model tool args had FRI and WED, but applied preferences retained only WED. | Important negative result preserved; model argument quality ≠ final applied constraints. |
| Step 133, Nov 4 | Trusted reconstruction for adding mandatory day; fail-closed continuity check and regression tests; actual three-turn local Ollama/Chromium validation. | Wednesday/Friday preserved, but CIS376 excluded; partial proposal contained online CIS410 only. First live probe failed its erroneous full-schedule assumption and was retained. |
| Step 134, Nov 4 | Optimistic context revision, stale concurrent response rejection and fixed retry UX, 18 concurrency tests. | In-process concurrency test only; no live multiworker load. |

## 6. Most recent full validated checkpoint

**CONFIRMED repository:** `cadomyetz79/una-mcp-unified-scheduler`, feature branch `integration/browser-gateway-20261102`, commit **`29e031554a20baf05cbb46fe351713eba5c2a03e`** — `fix(gateway): reject stale concurrent scheduling results` (Nov 4 local / Nov 5 UTC). Draft PR #3 remains open; eight GitHub checks for this commit were independently verified successful. No merge into team `main` is claimed.

**CONFIRMED Step 134 at this checkpoint:**

| Independent measurement | Observed result | Interpretation |
| --- | --- | --- |
| Focused optimistic concurrency | **18 passed** | Contained within root suite; no double count. |
| Full MCP/gateway root tests | **299 passed** | Offline synthetic tests. |
| Full AI-agent tests | **1,073 passed, 1 skipped** | Separate suite; scripted/offline tests. |
| GitHub Actions checks | **8/8 success** | Includes repeated workflow checks; not eight distinct model trials. |
| Chromium UI smoke | **Passed** | Mocked/intercepted HTTP for conflict/retry and UI cases. |
| Live local Ollama/Chromium three-turn continuation | **Exit 0; passed** | Sequential synthetic identity/MCP/Mock Banner demonstration; not concurrent model stress. |

**CONFIRMED three-turn scenario:** Student S10001 requests CIS376 + CIS410 with Friday mandatory; next prefers after 10:00 AM (stored as soft earliest 10:01); next adds Wednesday as mandatory. The final verified planner retains **WED and FRI required**, **earliest_start 10:01 soft**, and **requested course set CIS376/CIS410**. Under mock capacity/meeting constraints, **CIS376 has no feasible section**; online CIS410/SEC2002 is proposed as a **partial option**. The full two-course schedule is **not feasible under the tested constraints**. Existing registrations were not changed.

**CONFIRMED concurrency behavior:** Snapshot and revision are read atomically; a successful save increments revision; cardless responses check validity; stale requests return HTTP 409 without leaked model content/cards; invalidated sessions return 401. No lock is held during the model/tool call. Only single-process correctness is demonstrated.

## 7. Historical evaluation results — deliberately not pooled

| Source and revision | Recorded observation | What it does **not** prove |
| --- | --- | --- |
| WS1 Mock Banner historical component | 28 API tests passed (dated phase). | Not whole-agent reliability or live Banner. |
| Team WS3 frozen heldout2 | **23/37 (62.2%)** task successes on each of two CPU runs (qwen3:8b, historical code). | Not the post-integration quality rate or an independent benchmark after fixes. |
| Personal n8n tool-selection study | 16/16 scored predetermined tool/argument cases in Round 02; other studies had fixed repeated prompts. | Not necessarily correct student-facing claims. |
| Step 129 current model narrow two-turn repeat | **3/3** successful under identical synthetic prompt and model conditions. | Not statistical reliability across realistic varied requests. |
| Step 131 varied follow-ups | Five scenarios all completed; start-time accepted; day-addition exposed continuity defect; add/remove calls withheld cards; ambiguous did not plan. | Not a 5/5 functional success rate. Defect subsequently repaired. |
| Step 133 post-fix local live trial | Trial 1 exited 1 because probe expected no partial options; trial 2 passed. | Not two clean passing probes. The initial output remains part of evidence. |
| Step 134 concurrency | 18 tests passed, 299 gateway passed, 1,073 agent passed + 1 skip. | Not a deployed multiworker trial or production security certification. |

**Research conclusion permitted by evidence:** The current prototype demonstrates that a bounded conversational AI interface can invoke authorization-checked read-only MCP academic services and a deterministic planner under synthetic identity and course data, while safeguards reject some incorrect model output and protect continuity/session state. Negative results show that tool selection and grounding alone do not guarantee complete academic answers or constraint continuity.

**Claims not permitted:** "Production Entra integrated", "deployed for UNA students", "full Banner connectivity", "real OCR successfully ingested transcripts", "live RAGFlow retrieval running through Leo", "registration completed", "all schedule requests succeed", or "100% accuracy" without the narrow Step 129 qualifier.

## 8. Security, privacy, reproducibility and limitations

**CONFIRMED tested controls:** signed synthetic JWT verification; student binding; protected MCP authorization; refusal of recognized foreign academic record requests before model and MCP; origin and CSRF checks; short-lived opaque HttpOnly secure cookies; callback PKCE/replay protections; session revocation and expiry; bounded immutable PlanContext; one-plan and proposal-card provenance check; safe DOM rendering of model text; continuity guard preserving required restrictions; optimistic session revision on overlapping requests; no real enrollment writes.

**OPEN production gates:** Institutional Entra app registrations and student mapping, credential management, network segmentation of APIs and MCP, encrypted distributed session persistence and revocation, campus identity and FERPA/data policies, official Banner API contract/permissions, threat model and external security review, production observability and recovery.

**Reproducibility:** Preserve model name/digest, temperature, fixture hashes, commit SHA, script, actual runtime, output and exclusions for each evaluation. Do not overwrite earlier run evidence; do not confuse a source import test with live end-to-end behavior. Public artifacts must be sanitized and team-approved before publication.

## 9. Integration disposition as of Nov 4

| Subsystem | Prototype state | Remaining decision / proof |
| --- | --- | --- |
| WS1 Mock Banner data/API | **CONFIRMED** synthetic GET backend used in integrated path. | API schema approval and live Banner replacement are institutional, out of present research prototype scope. |
| WS2 protected MCP | **CONFIRMED** six read-only tools and synthetic authorization integrated. | Real Entra credentials/network deployment not verified. |
| WS3 AI agent and deterministic schedule validation | **CONFIRMED** integrated and repeatedly unit-/browser-tested. | Quality across unseen multi-turn prompts and partial proposal UX. |
| Leo browser UI | **CONFIRMED** synthetic HTTPS browser demo; cards, logout and safe responses; draft PR. | Deterministic partial-course exclusion labels should be visible from verified planner data, not solely model prose. |
| Session and multi-turn context | **CONFIRMED** bounded start-time/day-addition grammar, continuity and race protection. | Course add/remove, mixed soft/hard per-day semantics, durable intent, multiworker session storage are not supported as general features. |
| RAGFlow knowledge | **CONFIRMED contract import + offline tests.** | Live approved dataset, credentials, retrieval through final unified Leo agent **OPEN**. |
| OCR document intake | **CONFIRMED synthetic evidence validator contract + tests.** | Actual OCR conversion, provenance review and final assistant usage **OPEN**. |
| Evaluation and research paper | **CONFIRMED** substantial dated evidence, historical heldout2, reproducible demos. | Freeze final cross-workstream evaluation, choose paper claims, finish manuscript. |
| Master SOT | **CONFIRMED** full-source v1.2 archival draft + additive register. | Full line-by-line reconciliation, document QA, and team sign-off **OPEN**. |

## 10. Prioritized completion gates for Thursday, Nov 5, 2026

### Must finish for an academically defensible synthetic research prototype

**Gate A — freeze and reproduce (P0, 30–60 min).** Verify local clone and remote `29e0315` checkpoint, PR #3 status and CI; confirm synthetic no-enrollment demo startup and final repo cleanliness. Do not assume the unfinished Codex task changed the branch if no new commit appears.

**Gate B — clarify partial proposals (P0, 1–2 h).** Ensure Leo directly shows planner-verified *requested vs proposed vs excluded* courses, and deterministic `NO_SECTION_MATCHES_PREFERENCES` explanation in cards. Do not label CIS376 scheduled if only CIS410/SEC2002 is proposed. If not implemented by tomorrow, treat as a documented usability limitation and use a scripted explanation during the demo rather than make broad safety claims.

**Gate C — final integrated acceptance run (P0, 1–2 h).** Run full MCP/gateway and AI suites, browser smoke, one fresh live Ollama/Chromium 3-turn sequence, one synthetic foreign-student denial, logout/expiry, and one unsupported request. Preserve exact command, model version, fixture SHA, logs and observed outcomes. Recheck CI at new commit if code changes. Keep the real-Entra/Banner limitations clearly disclosed.

**Gate D — define knowledge-service boundary (P0 decision, 30–60 min).** Confirm with professor/team whether live RAG/OCR demonstrations are required in the final prototype. If *not* required, formally mark contracts tested but integration deferred, with rationale; the original research question does not explicitly require RAG/OCR. If required, allocate a separate explicit integration/test gate and do **not** claim they are present without real smoke-test evidence.

**Gate E — SOT review and source reconciliation (P0, 1–2 h).** Review this v1.3 draft alongside full-source v1.2 Word document, original WS1–WS4 documents, personal v1.7, inventory and register. Correct attribution and discrepancies; record reviewer/acceptance. Do not delete archival source content. Record whether Master SOT is formally adopted or remains draft.

**Gate F — paper and demonstration readiness (P0, 2–3 h).** Freeze architectural diagram, five-minute research demo, methods/results tables with exact denominators, three principal findings, limitations, proposed future work, and early-December manuscript outline. Assign paper sections and an owner to each. Collect screenshots that show synthetic labels and no enrollment.

### Stretch after essential goals

**P1:** Safe course add/remove follow-ups with explicit semantics and context revision; create regression tests before implementation. **P1:** Newly frozen unseen prompt suite; sample size and scoring rubric declared *before* runs. **P1:** Live RAGFlow policy retrieval and real OCR pipeline only if a rubric requires them. **P2:** Production Entra/Banner, shared multiworker session store, institutional approval and real-student trials are *not* credible one-day requirements.

### Finish/no-finish definition for tomorrow

Call **"synthetic MVP demo complete"** only when end-to-end execution, safety regressions, partial-case explanation, source-linked SOT and student-facing proposed-only labels are verified at a fixed commit. Call **"research paper complete"** only when a separate full manuscript exists, references and evidence are reviewed, and team/professor submission requirements are satisfied. **Do not call the official UNA-integrated system complete** without approvals and real infrastructure.

## 11. Open question register and decision owners

| Priority | Unresolved decision | Responsible reviewer / required evidence |
| --- | --- | --- |
| P0 | Is the original research question satisfied by a simulated Entra integration for the lab deliverable? | Professor + WS2/WS4; explicit scope acceptance. |
| P0 | Are RAG/OCR operational demonstrations required or optional future work? | Professor + relevant workstream owners. |
| P0 | What is the required final paper format, page count, citation style and submission date? | Professor / team; capture rubric. |
| P0 | Has the v1.2 full-source archive been line-reconciled with v1.7 and WS1–WS4 originals? | SOT editor + four workstream reviewers. |
| P0 | Does the user-facing partial-proposal UI show verified exclusions, not solely model explanation? | UI/integration owner; test and screenshot. |
| P1 | Who authorizes merging draft PR #3 into `main`? | Team repo owner and reviewers; do not merge unapproved. |
| P1 | How are requested-but-unsatisfied courses and pending intent retained across later turns? | WS3/UX owner; design with versioned context. |
| P1 | How should course add/remove and distinct soft/hard day constraints behave? | WS3 and professor; formal grammar/spec before code. |
| P1 | Can one newly frozen unseen dataset show post-integration behavior without contamination? | Evaluation owner; independent scoring rubric. |
| P2 | Who controls university tenant, Banner student mapping, student records and official deploy? | University technology/registrar/security; beyond synthetic project. |

## 12. Workstream review / signatures

**WS1 — William:** review Mock Banner route counts, fixtures, data authority, and academic backend statements: **PENDING**.  
**WS2 — MCP / identity coordination:** review protected six-tool contract, security boundaries, Git provenance and synthetic Entra wording: **PENDING**.  
**WS3 — Hassan:** review planner algorithm, partial options, rule semantics, heldout2 evaluation and current output claims: **PENDING**.  
**WS4 — Bryson:** review authorization tests, reproducibility, security gaps and deployment disclaimers: **PENDING**.  
**Professor / project sponsor:** confirm synthetic-versus-real scope and final paper rubric: **PENDING**.

No reviewer sign-off has been inferred from CI success or prior PR merges.

## 13. Supporting references and append-only continuation rules

**Primary integrated source:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/tree/29e031554a20baf05cbb46fe351713eba5c2a03e  
**Draft PR:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/pull/3  
**Step 133 research:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/research/2026-11-04-leo-weekday-continuity.md  
**Step 134 research:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/research/2026-11-04-leo-context-concurrency.md  
**Step 129 repeatability:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/research/2026-11-04-leo-live-repeatability.md  
**Imported RAG/OCR contracts:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/research/2026-11-02-unified-ragflow-ocr-contracts-import-1141-passed.md  
**Source-history master:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/sot/source-history/UNA_MCP_Team_Master_Source_of_Truth_v1.0_DRAFT.md  
**Decision register:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/sot/reconciliation/2026-11-02-unified-implementation-decision-register.md  
**Full-source Word draft:** https://github.com/cadomyetz79/una-mcp-unified-scheduler/blob/29e0315/docs/sot/master/UNA_MCP_Team_Master_SOT_v1.2_FULL_SOURCE_CONSOLIDATION_DRAFT.docx  
**WS1–WS4 original workstream source documents:** see section 3 and the full archived source inventory.

**Next update protocol:** preserve v1.2 and originals unchanged; append dated owner/commit/branch/goal/procedure/result/error/fix/security implication/evidence/classification/next decision. Promote this v1.3 synthesized draft to canonical only after full-source reconciliation, reviewer agreement and explicit version decision. Record any new phase as v1.3.x addendum or the adopted successor; never silently revise a failed historical run.

---

## Addendum — Phase 135A: Professor's Entra/MCP/RAG authorization handout (2026-11-05)

**Document-control notice:** This is an append-only update to the v1.3 **Markdown** working draft. The previously generated Word v1.3 document is a snapshot from before this addendum; it is not silently treated as synchronized. The comprehensive v1.2 full-source archive remains preserved and unaudited for final adoption.

**Original research question unchanged:** “How do we create an MCP server integrated with Entra and an AI agent to help schedule classes for students at UNA?”

**CONFIRMED source requirements:** The professor's new 15-page handout requires trusted `tid`/`oid`/`roles`/`groups`/`scopes` context, MCP RBAC at invocation, ingestion-time document ACLs, authorized vector/SQL candidate filtering, and final chunk/row checks before model access, with revocation and negative tests. PostgreSQL/pgvector is illustrative, not mandatory for a different deployed RAGFlow engine.

**CONFIRMED implementation:** In the current unified feature branch, source `src/mcp_server/entra_rbac_acl.py` and test `tests/test_entra_rbac_acl.py` were committed through `9b40c7d`. The isolated pure policy layer includes default-deny tool rules, correct ANY/ALL role/group semantics, group-overage refusal pending trusted resolution, tenant-scoped document ACLs with canonical hash/version, candidate document prefilter and returned chunk verification. **7/7 GitHub checks passed** on that test commit.

**CONFIRMED boundary:** These are tested **contracts**, not a completed RAGFlow authorization integration. Existing read-only MCP and RAGFlow adapters continue unchanged. No live Entra tenant, approved institutional roles, protected-document ingestion, RAGFlow-specific metadata filter, PostgreSQL/RLS deployment, or live five-user retrieval matrix was verified.

**WORKING ASSUMPTION:** The new policy contracts can be integrated without weakening the existing student-ID/CSRF/MCP/answer-grounding boundaries.

**OPEN QUESTION:** Securely propagate verified roles/groups into MCP and retrieval; identify actual RAGFlow version and vector backend; implement documented ACL and ingestion quarantine; verify pre- and post-filtering on real synthetic retrieval; define group refresh and policy version propagation.

**RECOMMENDATION:** Complete gated phases 135B (MCP RBAC), 135C (synthetic ACL ingestion), 135D (actual RAGFlow filter + chunk verifier), and 135E (five-identity integrated negative/positive tests). Preserve all test denominators and failures. See `docs/research/2026-11-05-entra-rag-authorization-phase135.md` and the append-only decision register for primary implementation provenance.


## Phase 135B — 2026-11-05 security/integration

## CONFIRMED
All six academic MCP handlers call server-owned role/scope authorization before
backend access. Trusted deployment tenant/audience/issuer are checked; mapped
student identity is required, and student-specific ownership remains independent.
Unknown tool policies deny. Synthetic legitimate fixtures explicitly carry
RAG.Student. No production UNA role assignments were invented.

The Phase 135A normalizer now rejects non-finite expiry, malformed group-overage
indicators, unbounded/control-character claim values, and contradictory
public/authenticated ACLs containing restrictive predicates. Group-dependent
authorization fails closed without Graph resolution. Safe logs contain only
allow/deny decisions, not tokens, identity fields, prompts, or records.

Tests: .venv/bin/python -m pytest -q tests/: 370 passed.
cd ai-agent && ../.venv/bin/python -m pytest -q: 1073 passed, 1 skipped.
Focused pre-regression run: 44 passed. New execution tests exercise all six
handlers against Student/Faculty/HR/Finance/Legal fixture roles, group revocation,
unknown tools and malformed claims. Signed HTTP MCP tests deny non-student roles
even when tools are advertised. Existing signature/expiry/audience/tenant tests
remain in the full root suite.

Changed paths: src/mcp_server/{entra_rbac_acl,team_security,team_protected_server}.py;
tests/test_entra_mcp_execution.py; protected MCP/browser integration fixtures;
synthetic scripts/leo_* and live_team_mcp_chat.py.
Evidence: docs/evidence/2026-11-05-135b-{root,agent}.txt.
No real Entra tenant or enrollment operations were used.

## WORKING ASSUMPTION
RAG.Student is the synthetic academic policy role; production configuration
requires institutional approval. Refreshed tokens are evaluated per request;
existing unexpired JWTs do not provide immediate directory-revocation detection.

## OPEN QUESTION
Microsoft Graph membership resolution and real university role provisioning remain
unavailable. The original professor handout was not found in searched local
Documents/attachments/home paths; the committed phase135 summary is the source used.

## RECOMMENDATION
Proceed with pre-parse ACL validation, atomic synthetic ingestion, and explicitly
gated retrieval capability validation; never substitute an unverified backend
filter or empty candidate set for authorization.

CONFIRMED evidence handling: temporary logs were unavailable at preservation time; both suites were rerun directly into repository evidence files with the same counts.

Implementation SHA is indexed in the session closeout.


# Phase 135C — Synthetic ACL ingestion
Date: 2026-11-05 (America/Los_Angeles). Workstream: security/RAG integration.
Base implementation: 7e4f092db3ef7c595c55f1e0d30b5e409bba6942.

## CONFIRMED
src/agent/secure_ingestion.py validates explicit synthetic source URI, dataset/domain,
classification and DocumentACL before invoking the parser. Each segment is a
separate document ID; complete ACL/provenance and a content digest accompany every
derived chunk. No OCR, real document, or remote vector writes are claimed.
Atomic staging prevents partial writes after parser failure. Revisions detect
policy changes during parsing. Versioned updates invalidate old chunks; revocation
removes chunks and prevents re-ingestion under the revoked record.

Tests: .venv/bin/python -m pytest -q tests/test_secure_ingestion.py: 13 passed.
Full root suite: 383 passed. Evidence: docs/evidence/2026-11-05-135c-*.txt.
Phase 135B exact-SHA GitHub workflows were all completed successfully when checked.
Original handout remains unavailable locally; committed summary guides this phase.

## WORKING ASSUMPTION
Separate source segments with independent ACLs are the minimal safe representation
for mixed permissions. The registry is an authoritative in-memory synthetic
contract, not a durable production database or actual RAGFlow ingestion.

## OPEN QUESTION
Remote metadata propagation, transactional vector publication, durable recovery,
real source ownership and approved corpus access require live backend validation.
Windows Docker daemon is unavailable and no WSL RAGFlow port is listening.

## RECOMMENDATION
Do not activate HTTP protected retrieval from source inspection alone. Require
deployment-specific prefilter evidence, use an explicit nonempty authorized
document list, and independently check returned metadata and content provenance.

Final implementation SHA is indexed in session closeout.


# Phase 135D — Authorized retrieval and Leo policy branch
Date: 2026-11-05 (America/Los_Angeles). Workstream: security/RAG/agent.
Base: 1a9520738d3af57a71913824f548c2ecfa657d93.

## CONFIRMED
AuthorizedKnowledgeRetriever derives document candidates from trusted identity,
dataset/domain allowlists and active ACLs before backend ranking. Empty candidate
sets make no backend call. Each returned chunk must match the authoritative
document, dataset, tenant, full ACL fields, version, hash, source URI and stored
content digest; unexpected chunks are discarded. Catalog changes during retrieval
abort the response. The synthetic backend is lexical ranking, not vector retrieval.

ProtectedRAGFlowBackend sends explicit nonempty document_ids/dataset_ids and asks
for document_metadata. It disables graph, compilation, highlight and TOC expansion.
It is disabled by default until trusted deployment prefilter validation; controlled
MockTransport tests exercise the HTTP contract. No live attestation is configured.

The optional Policy: branch in AuthenticatedSchedulingRunner re-verifies identity
before retrieval, before model access and before response. Only university/student
policy domains can be exposed to Leo. The model receives authorized excerpts and
can select only existing source IDs with no tools. Student output is deterministically
assembled from selected excerpts, not generated eligibility/registration claims.
Invalid model source/tool selections produce no selected evidence. Scheduling
requests continue through protected MCP and deterministic Banner planning.

Local RAGFlow checkout: v0.27.2, a024bea0cd93f39e6652a42bf84dd20c55bc560b.
Configuration defaults to Elasticsearch and image infiniflow/ragflow:v0.27.2.
No running installation was verified: WSL has no RAGFlow listener; Docker is absent
there, and Windows Docker reports its Linux engine pipe unavailable.
Inspected local chunk_api.py and reference_metadata_utils.py: document_ids reaches
the retrieval call; metadata is returned as document_metadata. Child expansion
occurs after retrieval, so deployment-specific pre-ranking guarantees must be
verified rather than inferred from this source inspection alone.

Official API reference documents document_ids and metadata_condition:
https://ragflow.io/docs/http_api_reference (accessed 2026-11-05).
The implementation uses an explicit trusted document list rather than model-created
metadata syntax. It does not claim a protected live RAGFlow deployment.

## Tests and corrections — CONFIRMED
Initial focused run: 33 passed, 1 failed (fixture RAG.Hr differed from required
RAG.HR). Corrected the synthetic fixture; original output retained.
Final focused run: 37 passed. Full root: 420 passed.
Full AI-agent: 1073 passed, 1 skipped.
Evidence: docs/evidence/2026-11-05-135d-*.txt.
Tests check all five classroom identities, actual candidate/result IDs, group
revocation/overage, direct-user ACL, empty candidates, forged metadata/content,
transport failures, source selection escalation and unauthorized text absent from
captured model messages. Phase 135C exact-SHA GitHub workflows all succeeded.

## WORKING ASSUMPTION
Authoritative local content hashes are suitable for the bounded synthetic corpus.
A live ingest adapter must register actual remote chunk IDs/text after approved
ingestion; arbitrary remote chunks cannot be accepted based only on a document ID.

## OPEN QUESTION
Live backend prefilter attestation, remote ingestion metadata parity, credentials,
Graph membership refresh and institutional role assignments remain unavailable.
The old RAGFlowRetriever remains a public/synthetic-only transport contract;
protected Leo uses the new authorized wrapper, never the legacy search method.

## RECOMMENDATION
Keep protected HTTP access disabled until version/backend-specific canary tests
prove pre-ranking restriction and metadata propagation. Preserve exact candidate
IDs and rejected-result cases; do not pool this synthetic matrix with heldout tasks.

Final SHA is indexed in session closeout.


# Phase 135E — signed synthetic identity matrix (2026-11-05)

## CONFIRMED
The reproducible scripts/authorized_knowledge_demo.py creates ephemeral signing
material, verifies each of five synthetic JWT identities, evaluates all six
academic MCP tool policies, and records the actual retrieval candidates/results.
Student permits six academic tools and retrieves public/student documents.
Faculty, HR, Finance and Legal each deny all six academic tools and retrieve
only public plus their own authorized document. Every matrix assertion passed.
No bearer tokens, private keys, real identities or enrollment operations are
included in evidence. This is a signed local fixture, not live Entra or RAGFlow.

Validation: five-identity matrix passed; targeted security suites 166 passed.
Evidence: docs/evidence/2026-11-05-135e-five-identity-matrix.json and
docs/evidence/2026-11-05-135e-security-tests.txt.
Phase 135D SHA 75c37a6c3b504feb7f1932f7fe572a8c3dfba0c3 has five completed
successful GitHub workflow runs.

## WORKING ASSUMPTIONS
These classroom roles illustrate isolation; institutional assignments require
review. Current-token checks do not imply immediate directory revocation.

## OPEN QUESTIONS
No running RAGFlow service or approved institution identity configuration is
available. Live backend filter behavior remains unverified.

## RECOMMENDATIONS
Retain this synthetic matrix separately from heldout evaluation and require
backend-specific prefilter canaries before enabling protected HTTP retrieval.
Final phase SHA is indexed in closeout.


# Phase 135F — Leo live integration closeout (2026-11-05)

Starting feature checkpoint: `ab5056b`.
Workstream: unified Leo UI, scheduling continuity, authorization integration.
Research question remains unchanged.

## CONFIRMED

- The unfinished Phase 135F changes add deterministic partial-proposal
  and exclusion metadata to authenticated verified schedule cards.
- Leo displays the exclusion reason directly from verified planner data.
- The first live trial failed after a valid first-turn schedule because
  context revalidation attempted to reproject a model-visible trace
  from which `student_id` had intentionally been removed.
- The correction independently compares requested courses, exclusion
  codes, trusted reason mappings, and proposal completeness with the
  trace, while preserving the authenticated-student checks.
- A later protected-knowledge browser attempt failed because its
  test expected chunk-only IDs instead of dataset/document/chunk IDs.
  Another test assertion expected a generic blocked record rather
  than the actual `system_privacy` denial.
- These test expectations were corrected without weakening access
  controls or changing application retrieval permissions.
- Live five-turn Chromium + Ollama synthetic trial passed:
  three scheduling turns, an authorized policy query, and a denied
  foreign-student-record request.
- Wednesday and Friday mandatory restrictions and the 10:01 soft
  start preference were preserved.
- Final proposal contained CIS410 SEC2002; CIS376 was excluded
  with `NO_SECTION_MATCHES_PREFERENCES`.
- Logout revoked the authenticated browser session.
- The foreign-student request used zero model calls.
- Final root suite: 432 passed.
- Final AI-agent suite: 1,073 passed, 1 skipped.
- Focused security/context tests: 57 passed.
- These test counts overlap and must not be added together.

## CONFIRMED evidence and changes

Source files:
`scripts/leo_browser_smoke.py`,
`scripts/leo_live_ollama_browser_probe.py`,
`src/gateway/leo_ui/unified.js`,
`src/gateway/plan_context.py`,
`src/unified/plan_cards.py`,
`tests/test_unified_plan_cards.py`,
`tests/test_gateway_verified_plan_context.py`.

Sanitized live result:
`docs/evidence/2026-11-05-135f-final-live-summary.json`.

Test output:
`docs/evidence/2026-11-05-135f-final-root.txt`;
`docs/evidence/2026-11-05-135f-final-agent.txt`.

Original failed attempts and full new live trial files remain in
the local research-evaluations/evidence directories.
A Phase 135F recovery archive was created before source edits.
This checkpoint does not overwrite historical evidence.

## WORKING ASSUMPTION

The bounded synthetic browser workflow is suitable for demonstration,
but a single successful live five-turn run is not a reliability estimate.

## OPEN QUESTIONS

- Live protected RAGFlow pre-ranking filter behavior remains unverified.
- The actual UNA Entra tenant, Graph group refresh, production Banner,
  real institutional policies, and student enrollment are not connected.
- The research prototype still needs the live RAGFlow integration phase.

## RECOMMENDATION

Commit this checkpoint after staged-file review. Keep PR #3 draft.
Start RAGFlow with synthetic data only, and verify authorization filters
before enabling protected HTTP retrieval. Record exact CI results
after the new commit is pushed.


## Step 138 A through D — 2026-11-07 — unified security and retrieval

CONFIRMED: Restored the localhost-only RAGFlow v0.27.2 / Elasticsearch lab,
legitimately provisioned a synthetic account, and indexed two separate six-document
canary corpora with local nomic-embed-text embeddings. Actual top-1 HTTP tests
returned the Legal decoy unrestricted, and the lower-ranking authorized document
when document_ids restricted candidates. Five role matrices and post-retrieval
metadata/content verification passed. Default protected backend stays disabled;
the explicit lab factory reruns canaries and limits Leo to public/Student sources.
Atomic remote-ID binding rejects content/ACL mismatches.

CONFIRMED: root 454 passed; agent 1073 passed, 1 skipped; overlapping security
selection 112 passed. Initial 5 harness failures and correction are preserved.
Starting SHA 748df1b7452339d6706a326ada81fc76ce6c2236.
Details, exact files, commands, provenance, errors and evidence:
docs/research/2026-11-07-step138-live-ragflow-authorization.md.

WORKING ASSUMPTION: bounded synthetic canaries detect relevant filter regressions.
OPEN QUESTION: production identity, continuous attestation, larger corpora and
durable policy synchronization remain unverified.
RECOMMENDATION: keep institutional activation gated; rerun after deployment changes.
Historical Phase 135 statements remain dated evidence, superseded only for these
specific live synthetic findings. Team Haystack code and results stay separate.


## Step 138 E through H — 2026-11-07 — unified integration closeout

CONFIRMED: Two real Chromium/Ollama trials passed with actual RAGFlow HTTP policy
retrieval. Final model calls by turn were 3, 2, 2, 1, 0. Wednesday plus Friday
mandatory restrictions and the soft 10:01 preference persisted; CIS376 exclusion
was deterministic. Foreign-student denial used zero LLM calls; logout revoked
the session. Explicit lab configuration reruns canaries; production defaults
remain disabled and Leo can access only public/Student canary documents.

CONFIRMED: Final root 455 passed; agent 1073 passed, 1 skipped; overlapping
security subset 113 passed; browser smoke passed. A document-contained prompt
injection regression rejects privileged source/tool selection. Original failed
runs remain evidence. Library SHA 0c04434906c5118d1168d2743dae4c85daba05b3 has
4 successful workflows / 7 successful jobs. Final integration SHA and CI are
verified after commit. PR stays draft; only origin feature branch is authorized.

Full phase matrix, files, measured results, limitations and paper-ready findings:
docs/research/2026-11-07-step138-leo-closeout.md.
Exact procedures: docs/research/2026-11-07-step138-runbook.md.
Evidence prefix: docs/evidence/2026-11-07-138-.

WORKING ASSUMPTION: the bounded canary is a useful regression gate.
OPEN QUESTION: institutional deployment, durable policy state and continuous
backend assurance are not established.
RECOMMENDATION: broaden adversarial evaluation and obtain owner review before
institutional data or any production activation. Preserve the unchanged original
research question and separate teammate Haystack, offline, live HTTP and browser
evidence categories.


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


## Step 142 — 2026-11-07 — interactive Leo and RAGFlow

**CONFIRMED:** A separate localhost-only interactive
launcher connects Leo, Ollama, protected MCP, synthetic
Mock Banner and real RAGFlow HTTP retrieval. The
existing scheduling-only launcher remains unchanged.

**CONFIRMED:** User-observed manual tests demonstrated
scheduling, retrieval of an authorized synthetic policy
excerpt, restricted-content non-disclosure, foreign
student refusal, and scheduling continuity after policy
questions. These are bounded manual observations.

**CONFIRMED:** The live RAGFlow authorization canary,
five-role matrix and cross-tenant check passed.
Regression results: 458 MCP/gateway tests passed;
1073 AI-agent tests passed and one skipped.

**WORKING ASSUMPTION:** The synthetic demonstration is
a valid modular architecture proof of concept, not a
production deployment or general security guarantee.

**OPEN QUESTION:** The RAG teammates' actual knowledge
base and ingestion work remain to be integrated.
Institutional Entra, Banner and document authorization
approvals are also pending.

**RECOMMENDATION:** Preserve the research evidence,
keep PR #3 draft, and verify the team's RAGFlow
configuration before replacing the synthetic corpus.

Research record:
docs/research/2026-11-07-step142-interactive-ragflow.md


## Step 145 — 2026-11-11 — final research scope and Haystack reconciliation (pending team verification)

**Original research question preserved verbatim:** “How do we create an MCP server integrated with Entra and an AI agent to help schedule classes for students at UNA?” The absence of live Entra/Banner access is a research limitation, not a reason to rewrite the historical question without instructor approval.

### CONFIRMED — user-reported final scope
- The team selected **Haystack**, rather than RAGFlow, as its intended RAG workstream for the final manuscript. This is a scope decision reported by the project integrator on 2026-11-11; the change is not evidence that Haystack has been incorporated into Leo.
- No approved real University of North Alabama Banner data or Microsoft Entra tenant sign-in will be obtained for this research phase. Synthetic Mock Banner and Entra-oriented synthetic signed JWT/role/group authorization remain the demonstrated development basis.
- The professor-provided *Entra_ID_MCP_RAG_Authorization_Student_Handout.docx* provides a synthetic authorization model (claims → trusted security context; MCP tool policy; document ACLs; prefilter; post-retrieval verification). It is not proof of working production SSO.

### CONFIRMED — GitHub evidence at inspection
- Unified feature branch `integration/browser-gateway-20261102` was inspected at `fb1500357c2b3d3de37f1ae46097a2aeb7950dc0`. The draft PR #3 remained open; the separate live five-question Leo+RAGFlow demo and synthetic authorized retrieval were recorded as passed. Its 458 root tests and 1,073 agent tests/1 skip were previously observed. The seven corresponding GitHub CI checks passed. **These results do not verify Haystack integration.**
- At the 2026-11-11 check, the connected GitHub account received HTTP 404 for `devink727/ite499-shared` (repository metadata, contents, commit list, and repository URL). A new full-source audit of that repo is **NOT POSSIBLE** with current access.
- An earlier, locally inspected copy of that RAG repository, recorded in the project history at SHA `7ef1b01`, contained `README.md`, `main.py`, `pipeline.py`, `security_policy.py`, `test_harness.py`, `requirements.txt`, `.env.example`, and `.gitignore`. The archived source-review transcript (2026-11-06 04:29:44) records `haystack-ai==3.2.0`, FastAPI `POST /query`, `InMemoryDocumentStore`, `InMemoryBM25Retriever` with tenant/ACL metadata filters, `ChatPromptBuilder`, and `OpenAIChatGenerator(model='gpt-4o-mini')`. Its demo authentication used two fixed mock tokens, **not Microsoft-issued Entra tokens**. Eleven named `unittest` methods in `test_harness.py` covered roles, groups, users, malformed claims, and cross-tenant isolation; inspection identified the tests, but no fresh execution/score is established by this review. This is a **separate Haystack workstream**, not evidence of a successful unified Haystack+Leo conversation.
- The integrated `fb15003` Leo application used the existing RAGFlow-backed `Policy:` branch. Consequently the recorded five-turn live RAGFlow browser trial, startup authorization canary and screenshot are **RAGFlow evidence only**. Do not rename or pool these as Haystack observations.

### OPEN QUESTIONS / manuscript acceptance gates
1. Obtain an accessible final Haystack repository snapshot/ZIP and immutable SHA from the RAG workstream; reconcile any changes since the inspected `7ef1b01` snapshot.
2. Establish whether Haystack has actually been called by Leo or through a unified MCP-adjacent route. If not, describe component-level Haystack proof of concept and unified scheduling proof of concept separately, not as one tested RAG architecture.
3. Execute and preserve the Haystack test suite results (names, denominator, environment, date, exact SHA); distinguish offline ACL unit tests from retrieval-quality and generated-answer evaluation. If a paid OpenAI API is required but unavailable, report untested generation without fabricating it.
4. Confirm manuscript authorship, final instructor length/template/deadline and approved references before claiming a final submission-ready IEEE conference paper.
5. Obtain consent/approval before handling institutional records or deploying. No state-changing registration writes were implemented.

### WORKING ASSUMPTION / RECOMMENDATION
- **Working assumption:** The earlier Haystack snapshot still represents the team's current RAG design until newer accessible code says otherwise.
- **Recommendation:** Base the paper on two evidence-separated prototypes: (i) verified protected MCP, Mock Banner, Leo and deterministic schedule results; (ii) inspected Haystack metadata-filter retrieval security proof of concept. Retain the earlier live RAGFlow trials as labeled historical integration experiments, but do not present them as Haystack tests or as the final selected RAG implementation. Do not rewrite archival SOT records. Preserve PR #3 as draft, avoid team-upstream writes, and close these evidence gaps before final paper submission.

Reconciliation note: `docs/research/2026-11-11-final-scope-haystack-reconciliation.md`.
