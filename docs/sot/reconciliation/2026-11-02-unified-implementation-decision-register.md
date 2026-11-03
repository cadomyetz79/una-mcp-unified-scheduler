# Unified UNA MCP implementation — current-state decision register (draft)

**Date:** 2026-11-02 (local research phase). **Status:** DRAFT pending team review; append-only to the complete historical Master SOT v1.2. **Research policy:** This register does not replace the original team Master v1.0, personal v1.7, eight workstream documents or the generated 4,100-paragraph master draft; the source hashes and 516 archived source files are recorded in `docs/sot/drafts/SOURCE_INVENTORY_AND_VALIDATION.json`.

## Provenance and confirmed baselines

- **CONFIRMED** Official team source: `cadomyetz79/una-mcp-scheduler`, `main` at `a55813c464ac3b4587a935b63aae444219651222`. Team PR #29 (WS2 protected MCP + WS3 + WS1 integration) has merged into `main`; PRs #30, #34, #35, #36 and #37 also merged, so do not use the older PR #29 integration branch as the current baseline.
- **CONFIRMED** Personal research source: `cadomyetz79/una-mcp-scheduler-personal`, branch `research/authenticated-mcp-integration-20261029`, personal SOT `docs/UNA_MCP_Source_of_Truth_v1.7.docx`. This is a **separate** experimental implementation; its tests and browser demo are not automatically inherited by the team agent.
- **CONFIRMED** Master Source of Truth full-source draft: `docs/sot/drafts/UNA_MCP_Team_Master_SOT_v1.2_FULL_SOURCE_CONSOLIDATION_DRAFT.docx`, introduced to the private research branch at commit `6c35ad5`, **803** original personal paragraphs preserved, **19** tables preserved, **241** original team Master v1.0 Markdown lines included, **4,100** total Word paragraphs and **516** source files archived externally to the Word content. **VISUAL QA AND FACTUAL RECONCILIATION ARE OPEN**.
- **CONFIRMED** WS3 heldout2 evaluation performed two runs of 37 synthetic cases using qwen3:8b on CPU. **23/37** end-to-end succeeded in each run; model-prose and planning weaknesses remain. This is not a pass rate for the consolidated final application. See team `docs/evidence/2026-11-02-heldout2-report.md`.
- **CONFIRMED** Existing team code has independently passing CI for Mock Banner/MCP and agent tests on recent merged commits. The last user-observed WS2 PR phase ran local root **53 passed** and WS3 **874 passed, 1 skipped** before later team merges. Historical numbers are not the new combined baseline until rerun.
- **CONFIRMED** Personal research Phase 13 reported **784 passed, 11 skipped** in its own default suite, and a distinct opt-in browser+Ollama+protected personal MCP synthetic scenario passed; those results **do not** show that personal Leo currently calls the team WS3 planner.

## Consolidation architecture — selections

1. **RECOMMENDATION → implementation baseline:** Clone the *merged* team `main` into a distinct local working directory. Keep a read-only `team-upstream` remote. Do not edit or force-push either source repository; use a new **private** GitHub repository for the working unified implementation once local preflight succeeds.
2. **RECOMMENDATION:** Keep WS1's existing synthetic Mock Banner HTTP API (`app/main.py`, `data/`, `tests/test_api.py`) as test backend and retain its six-file fixture data as the source of record. Avoid parallel personal Mock Banner services in the live app.
3. **RECOMMENDATION:** Keep WS2's six read-only authenticated MCP tools (`src/mcp_server/`) and WS4 JWT/security checks (`tests/test_entra_token_verifier.py` and MCP boundary tests). The protected MCP server independently enforces student identity. Never add insecure academic-tool shortcuts to support UI convenience.
4. **RECOMMENDATION:** Keep team WS3 `ai-agent/agent/` as the single deterministic planner and model answer guard. Do **not** copy personal `src/agent/scheduling_workflow.py` over it: personal prototype assumes MCP tools including `generate_schedule_options` and `get_student_schedule`, while the team tool contract defines six read-only tools and computes plans in WS3 application code. An explicit adapter with tests is required.
5. **RECOMMENDATION:** Adapt personal Leo browser UX, simulated OAuth/session gates, and verified section-display UX **only after** implementing and testing a team-plan-to-view-model projection. The team planner `plan_schedule` result provides `options[].sections[]` including section/course IDs, modality and meetings, but the planner's `_describe()` does **not** include the course title or per-course credit hours. Never invent those: retrieve additional academic facts via trusted student-bound MCP and validate the join or omit the fields. Registration-fit/status labels must come from `registration_fit` and verified current registrations; never treat an option as an enrollment.
6. **RECOMMENDATION:** Add the personal RAGFlow adapter and `PublicKnowledgeRetriever` contract as **optional read-only public-policy knowledge** service, gated by allowlisted questions. Do not send student transcripts, tokens or confidential academic data into public-policy retrieval. Any team RAGFlow credentials and approved dataset IDs remain **OPEN**.
7. **RECOMMENDATION:** Reuse the personal `validate_synthetic_ocr_handoff` evidence schema and fail-closed student binding as an optional **non-authoritative** ingestion contract. Real OCR processing and record reconciliation remain **OPEN**. OCR findings must never become Banner truth or automatically satisfy prerequisite checks without approved verification.
8. **RECOMMENDATION:** Separate pure unit/contract tests, synthetic authenticated HTTP tests, live local model tests, and opt-in browser tests. Add quality cases from WS3 heldout2 as future **development tests** with versioned holdout sets; never modify the predeclared original outcomes retroactively.

## Immediate gated implementation plan

- **Gate A — Current source baseline:** New isolated checkout of team main at a55813c; first run root and WS3 offline suites; capture exact environment, counts, status and commit. **Not yet user-observed in new checkout.**
- **Gate B — New source history and safety:** Establish private GitHub origin without allowing a push to `team-upstream`. Carry full source provenance and Master SOT v1.2 as **private** artifacts. Keep original source repos untouched. **Not yet created.**
- **Gate C — First low-risk code imports:** Bring the personal public-policy retriever interface/RAGFlow adapter and synthetic OCR handoff **with their focused tests**, without wiring to the live browser, scheduling or authentication service. Verify combined regression and import/dependency compatibility before committing. **Not yet executed in unified checkout.**
- **Gate D — Trusted data display adapter:** Add fail-closed validated team-plan-to-view-model projection and tests. Verify section/credits/current-registration facts rather than assuming personal tool schema. **Not yet executed.**
- **Gate E — Leo and unified AI UX:** Build a single authenticated browser gateway calling team WS3 through team WS2, with RAG and OCR deliberately modular. Make startup opt-in; test synthetic cross-student isolation, CSRF, no token leakage, read-only. **Not yet executed.**
- **Gate F — Final integration research:** Re-run full regression, repeat representative local Ollama and browser trials, record known failure matrix, compare WS3 heldout2 scores on a newly declared evaluation set, and reconcile all master SOT classifications. Do not claim production readiness. **Not yet executed.**

## Open questions requiring team or UNA input

- Team owner approval of the effective six-MCP-tool and backend contract, especially student-ID/token mapping and actual Entra authority.
- Whether team RAG and OCR workstreams have verified runnable adapters and synthetic datasets; if so, compare against personal prototypes before selecting a final implementation.
- Official UNA-approved use of Banner, Entra, policy documents, student data, FERPA controls and brand assets.
- Final architecture approval and repository governance; who may access the new private repo; team review cadence.
- Exact retained historical source hashes; the manifest is the authoritative *integrity inventory* for its archived source files.

**No enrollment transaction is authorized or implemented by the confirmed integration. No claims of official UNA deployment or live student records.**

---

## STEP-49-TRUSTED-HANDOFF-2026-11-02

Date: 2026-11-02
Phase: Trusted AI assistant / plan-card integration

**CONFIRMED:** The unified scheduling assistant now
supports a request-scoped, optional trusted plan-card
projection separate from redacted model-facing data.

**CONFIRMED:** Projection failure is handled without
exposing exception details or interrupting a valid
scheduling answer.

**CONFIRMED:** Complete regression results:
128 MCP tests passed; 1040 AI-agent tests passed,
1 skipped.

**CONFIRMED:** No enrollment operations were added.

**WORKING ASSUMPTION:** A future gateway will provide
server-verified identity and term context.

**OPEN QUESTION:** Browser gateway, actual Leo UI
integration, approved production identity mapping,
and final master SOT reconciliation.

**RECOMMENDATION:** Review and merge the guarded
handoff through a pull request before building
the browser-facing integration.

Evidence and detailed decisions:
docs/research/2026-11-02-trusted-assistant-plan-card-handoff.md

The consolidated master SOT v1.2 remains a draft.

---

## STEP-56-UI-REFUSAL-CONSISTENCY-2026-11-02

**CONFIRMED:** Step 53 identified a mismatch between
a model refusal and displayed verified plan cards.

**CONFIRMED:** Step 54 added consistency checks but
revealed an incorrectly escaped refusal expression.

**CONFIRMED:** Step 55 corrected the expression and
passed 128 MCP tests plus 1044 AI-agent tests,
with one AI-agent test skipped.

**CONFIRMED:** No registration capability was added.

**WORKING ASSUMPTION:** Conservative answer matching
is suitable for the current synthetic prototype.

**OPEN QUESTION:** Comprehensive semantic consistency
and browser end-to-end behavior remain unverified.

**RECOMMENDATION:** Merge only after updated PR CI
and code review. Preserve all regression evidence.

Research:
docs/research/2026-11-02-plan-card-refusal-regression-closeout.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-63-AUTHENTICATED-GATEWAY-2026-11-02

Date: 2026-11-02
Phase: Authenticated browser gateway integration

**CONFIRMED:** Prior integration PR #2 was merged
into unified main at 77c21cc after all 10 GitHub
checks passed.

**CONFIRMED:** A separate FastAPI gateway foundation
and authenticated MCP/AI-agent runner have been
implemented and locally tested.

**CONFIRMED:** The signed synthetic integration test
exercises gateway authentication, student mapping,
protected MCP, deterministic scheduling, and
verified proposed-only plan cards.

**CONFIRMED:** Step 62 results: 137 MCP tests passed;
1044 AI-agent tests passed, 1 skipped.

**CONFIRMED:** Unauthorized synthetic requests were
rejected in the tested scenarios.

**CONFIRMED:** No enrollment capability was added.

**WORKING ASSUMPTION:** The future browser application
will use approved sign-in and server-bound identity.

**OPEN QUESTION:** Real Entra, live browser/LLM,
frontend, RAG/OCR orchestration, Banner replacement
and production deployment remain unverified.

**RECOMMENDATION:** Commit this verified gateway phase,
then implement and test the frontend on the same
feature branch before requesting a merge.

Evidence and implementation details:
docs/research/2026-11-02-authenticated-browser-gateway-integration.md

The master SOT v1.2 remains a consolidation draft.

---

## STEP-68-ORIGINAL-LEO-RESTORATION-2026-11-02

**CONFIRMED:** The original Leo design from the
personal MCP repository was recovered into the
unified browser-gateway feature branch.

**CONFIRMED:** The developer-selected lion-only
mark replaced the default preview logo and favicon.

**CONFIRMED:** Original source assets remain
preserved. The derived preview remains noninteractive
until authenticated session support is integrated.

**CONFIRMED:** No academic access or registration
bypass was introduced.

**WORKING ASSUMPTION:** The original purple-and-gold
Leo design is the canonical student-facing UI.

**OPEN QUESTION:** Secure browser sessions, CSRF,
approved sign-in, verified plan-card rendering,
and live browser/model behavior.

**RECOMMENDATION:** Reuse the private project's
session-security components with updated unified
MCP and agent response contracts.

Research:
docs/research/2026-11-02-original-leo-ui-restoration.md

Master SOT v1.2 remains a reconciliation draft.

---

## STEP-69-BROWSER-SESSION-FOUNDATION-2026-11-02

**CONFIRMED:** The original private MCP session
management components were adapted into the
unified gateway package.

**CONFIRMED:** Opaque session credentials, bounded
expiration, CSRF verification and rotation, and
revocation are implemented.

**CONFIRMED:** Session tests include two-student
isolation and denial of invalid credentials.

**CONFIRMED:** No browser login or session issuance
endpoint was activated.

**WORKING ASSUMPTION:** An in-process session store
is suitable for isolated synthetic research tests.

**OPEN QUESTION:** Approved OAuth callback, HTTPS
session endpoints, browser response integration,
and production session management.

**RECOMMENDATION:** Test exact-origin HTTPS requests,
CSRF enforcement, and delegated token revalidation
before enabling interactive Leo chat.

Research:
docs/research/2026-11-02-browser-session-foundation.md

Master SOT v1.2 remains a reconciliation draft.
