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

---

## STEP-71-SIGNED-SESSION-ROUTES-2026-11-02

**CONFIRMED:** Opt-in browser-session routes added
to the unified gateway.

**CONFIRMED:** Exact-origin HTTPS, CSRF, student
identity binding, delegated-token revalidation,
and session revocation are implemented and tested.

**CONFIRMED:** Locally signed synthetic JWTs are
used in additional browser-session security tests.

**CONFIRMED:** The default gateway continues
without session routes or a login issuer.

**WORKING ASSUMPTION:** A secure same-origin
browser session is the appropriate research UI
authentication architecture.

**OPEN QUESTION:** Approved Entra login flow,
signed session-to-protected-MCP integration,
and functional interactive Leo UI validation.

**RECOMMENDATION:** Keep the original Leo design
and adapt its client contract to verified unified
MCP schedule cards.

Research:
docs/research/2026-11-02-signed-jwt-browser-session-routes.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-73-LEO-INTERACTIVE-UI-2026-11-02

**CONFIRMED:** The original Leo interactive chat
design was adapted to the unified gateway contract.

**CONFIRMED:** The selected lion-only PNG and the
original purple-and-gold styling were preserved.

**CONFIRMED:** The adapted browser code uses
session bootstrap, CSRF-protected chat requests,
safe DOM rendering, and verified proposal cards.

**CONFIRMED:** The interactive page is exposed only
by explicit installation of browser session routes.

**CONFIRMED:** The Step 72 interface and complete
MCP regression suites passed.

**WORKING ASSUMPTION:** Leo remains the canonical
student-facing interface for the research project.

**OPEN QUESTION:** Complete signed browser-session
to protected MCP integration, approved OAuth login,
and real-browser interaction validation.

**RECOMMENDATION:** Complete signed end-to-end
testing before enabling live browser academic chat.

Research record:
docs/research/2026-11-02-leo-unified-interactive-ui.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-76-FULL-BROWSER-MCP-INTEGRATION-2026-11-02

**CONFIRMED:** A locally signed synthetic JWT
was verified before issuing a server-side browser
session in the integration test.

**CONFIRMED:** The test exercised browser-session
authorization, CSRF protection, the authenticated
gateway, protected MCP tools, and the real
deterministic scheduling planner.

**CONFIRMED:** Student S10001 received a verified
2027SP proposal containing SEC1001 and SEC2002.

**CONFIRMED:** Returned schedule cards remained
proposed_only, and no enrollment was performed.

**CONFIRMED:** Negative tests rejected unauthorized
browser requests before entering the AI runner.

**CONFIRMED:** Step 75 complete MCP regression
reported 175 passing tests.

**WORKING ASSUMPTION:** The unified backend can
support the original Leo interface after approved
browser authentication is implemented.

**OPEN QUESTION:** University-approved Entra login,
real-browser execution, live model integration,
and deployment security remain unverified.

**RECOMMENDATION:** Preserve the identity and
deterministic-planning security boundaries.
Complete real-browser testing before describing
the UI as operational.

Research:
docs/research/2026-11-02-full-browser-session-mcp-integration.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-78-LEO-STATIC-ASSET-POLICY-2026-11-02

**CONFIRMED:** The unified gateway previously
mounted the entire restored Leo asset directory.

**CONFIRMED:** Static access was restricted to
explicitly approved public assets.

**CONFIRMED:** Original HTML documents remain
preserved in Git but are no longer served through
the public static asset endpoint.

**CONFIRMED:** The approved Leo interface and
selected lion-only logo remain unchanged.

**WORKING ASSUMPTION:** An allowlisted public asset
surface is preferable to publishing the entire
restored source directory.

**OPEN QUESTION:** Complete graphical browser
validation and approved OAuth deployment remain.

**RECOMMENDATION:** Complete CI review and
browser interaction testing before merge.

Research:
docs/research/2026-11-02-leo-static-asset-security-review.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-81-LEO-BROWSER-VALIDATION-2026-11-02

**CONFIRMED:** Leo was visually inspected in
Microsoft Edge by the developer.

**CONFIRMED:** Headless Chromium executed the
interactive Leo JavaScript and rendered synthetic
schedule cards.

**CONFIRMED:** Browser tests covered simulated
session bootstrap, chat, logout, wrong-student
responses, and mobile layout.

**CONFIRMED:** The unused generic frontend and
its /assets route were retired.

**CONFIRMED:** The original Leo design and lion
branding remain the canonical UI.

**WORKING ASSUMPTION:** The restored interface
can support a future approved authenticated
research demonstration.

**OPEN QUESTION:** Real Entra sign-in, full
browser-to-MCP deployment, live LLM behavior,
and final institutional approvals.

**RECOMMENDATION:** Complete CI/security review
on this commit before merging.

Research:
docs/research/2026-11-02-leo-browser-validation.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-82-LEO-BROWSER-CI-2026-11-02

**CONFIRMED:** A dedicated automated Chromium
browser smoke workflow was added to GitHub Actions.

**CONFIRMED:** The test uses intercepted synthetic
HTTP responses, with no actual browser login.

**CONFIRMED:** Existing MCP and agent CI passed
for commit ace36b3.

**OPEN QUESTION:** The new browser workflow must
complete successfully on GitHub before its CI
status can be classified as passing.

**RECOMMENDATION:** Retain the draft PR until
browser CI and security review are complete.

Research:
docs/research/2026-11-02-leo-browser-ci-automation.md

---

## STEP-83-OAUTH-PKCE-FOUNDATION-2026-11-02

**CONFIRMED:** The original OAuth state/PKCE
foundation was imported into the unified gateway.

**CONFIRMED:** Its source content was preserved.

**CONFIRMED:** New synthetic tests cover state
correlation, PKCE, expiration, replay prevention,
redirect validation, and bounded capacity.

**CONFIRMED:** No OAuth login, callback, or token
issuance endpoint was installed.

**WORKING ASSUMPTION:** The original component
can be reused for the approved browser auth flow.

**OPEN QUESTION:** Actual code exchange, approved
identity provider configuration, and production
HTTPS deployment remain outstanding.

**RECOMMENDATION:** Keep PR #3 in draft while
authenticated browser sign-in is developed.

Research:
docs/research/2026-11-02-oauth-pkce-foundation.md

---

## STEP-85-OAUTH-CALLBACK-INTEGRATION-2026-11-02

**CONFIRMED:** Opt-in OAuth login and callback
routes were implemented using the existing
state/PKCE and browser-session components.

**CONFIRMED:** The callback requires an approved
configuration contract, valid state correlation,
trusted code-exchange result, verified JWT and
authorized student identity before issuing an
opaque browser session.

**CONFIRMED:** The Step 84 initial test suite
reported 9 passed and 1 failed due to an incorrect
expectation about missing-cookie state consumption.

**CONFIRMED:** Step 84A corrected the expectation
and added a separate wrong-cookie replay test.

**CONFIRMED:** Step 84A results were:
11 OAuth tests passed; 62 combined authentication
tests passed; 205 MCP tests passed; 1044 agent tests
passed and 1 skipped.

**CONFIRMED:** The default gateway still has no
active OAuth login or callback endpoints.

**WORKING ASSUMPTION:** This synthetic OAuth
contract can be adapted for approved Entra sign-in.

**OPEN QUESTION:** Actual Microsoft token exchange,
production session deployment, and complete
login-to-MCP validation remain unverified.

**RECOMMENDATION:** Perform a synthetic full
OAuth-login-to-protected-MCP test next.

Research:
docs/research/2026-11-02-oauth-callback-integration.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-87-FULL-OAUTH-MCP-INTEGRATION-2026-11-02

**CONFIRMED:** A single synthetic integration
test now exercises OAuth state/PKCE, fake code
exchange, signed JWT verification, browser session,
CSRF, authenticated AI gateway, protected MCP,
deterministic scheduling, and verified Leo cards.

**CONFIRMED:** Student S10001 received a 2027SP
proposal containing SEC1001 and SEC2002.

**CONFIRMED:** No enrollment was performed.

**CONFIRMED:** Missing CSRF, foreign origin,
browser-supplied identity, session reuse after
logout, and OAuth callback replay were rejected.

**CONFIRMED:** Local Step 86 results:
206 MCP tests passed; 1044 agent tests passed,
1 skipped; full OAuth-to-MCP test passed.

**WORKING ASSUMPTION:** The unified architecture
can support a future approved live Leo deployment.

**OPEN QUESTION:** Real Entra integration,
HTTPS deployment, persistent sessions, live-model
validation, and graphical browser-to-MCP operation.

**RECOMMENDATION:** Retain this integration test
and the associated evidence as a regression
baseline for the research paper.

Research:
docs/research/2026-11-02-full-oauth-to-protected-mcp.md

Master SOT v1.2 remains a consolidation draft.

---

## STEP-89-LOCAL-HTTPS-BROWSER-MCP-2026-11-03

**CONFIRMED:** A real Chromium browser successfully
connected to a running loopback HTTPS FastAPI gateway.

**CONFIRMED:** The synthetic OAuth callback issued
an authenticated student session, which was used for
a real HTTPS browser chat request.

**CONFIRMED:** Protected MCP academic handlers and
the deterministic scheduling planner executed.

**CONFIRMED:** Leo displayed a proposed schedule
containing SEC1001 and SEC2002 for synthetic
student S10001 in 2027SP.

**CONFIRMED:** Logout revoked the browser session.

**CONFIRMED:** Step 88 initially encountered import,
navigation and simulated-identity-provider issues;
the final corrected test passed.

**CONFIRMED:** The complete local MCP regression
reported 206 passing tests, and the AI-agent suite
reported 1044 passed with 1 skipped.

**WORKING ASSUMPTION:** The integrated research
architecture can support a controlled interactive
demonstration.

**OPEN QUESTION:** Approved Entra login, production
TLS, persistent sessions, independently deployed
MCP networking, live LLM, and final SOT consolidation.

**RECOMMENDATION:** Preserve browser evidence,
keep the PR in draft, and develop a controlled
manual synthetic demonstration environment.

Research:
docs/research/2026-11-03-local-https-browser-mcp-validation.md


### STEP-89A-EVIDENCE-WHITESPACE-CORRECTION

**CONFIRMED:** The browser demonstration and
regression suites passed before the initial
Step 89 commit attempt.

The commit stopped at `git diff --cached --check`
because Rich-formatted HTTP logging introduced
trailing whitespace in the captured evidence.

**CORRECTION:** Removed trailing whitespace only.
The successful test markers and results were preserved.
No application implementation changes were required.


---

## STEP-90-CHROMIUM-CI-RUNNER-2026-11-03

**CONFIRMED:** Commit 3fb58bf passed both
GitHub MCP integration checks.

**CONFIRMED:** The Chromium CI job failed during
dependency installation on Ubuntu 26.04 before
its browser tests executed.

**CONFIRMED:** The browser workflow was changed
from ubuntu-latest to ubuntu-24.04 for compatibility
with pinned Playwright 1.58.0.

**OPEN QUESTION:** The new GitHub workflow result
must be verified before it is considered passing.

**RECOMMENDATION:** Keep PR #3 in draft pending
successful browser CI.

Research:
docs/research/2026-11-03-leo-browser-ci-runner-fix.md


---

## STEP-92-MANUAL-LEO-DEMO-2026-11-03

**CONFIRMED:** The operator successfully used Leo
in Microsoft Edge with the local synthetic demo.

**CONFIRMED:** The displayed response contained
SEC1001 (already registered) and SEC2002 (proposed)
in 2027SP, totaling six schedule credits.

**CONFIRMED:** The UI reported no enrollment.

**CONFIRMED:** The separate manual demo launcher
was made self-contained for Python imports.

**WORKING ASSUMPTION:** This demonstration is
suitable for local research presentation when
identified as synthetic and scripted.

**OPEN QUESTION:** Live model, RAG/OCR, approved
Entra, separately deployed MCP, and SOT consolidation.

**RECOMMENDATION:** Preserve the manual test and
never expose the demo login as production auth.

Research:
docs/research/2026-11-03-manual-leo-demonstration.md

Evidence:
docs/evidence/2026-11-03-step92-manual-demo-observation.md


---

## STEP-96-LIVE-OLLAMA-MCP-2026-11-03

**CONFIRMED:** Step 95 demonstrated a real local
qwen3:4b-instruct model selecting and successfully
executing plan_schedule through protected MCP.

**CONFIRMED:** Two live-model calls occurred, one
model-selected planning operation succeeded, and
the agent returned a grounded answer.

**CONFIRMED:** The Chromium browser displayed
verified schedule cards through the HTTPS gateway.

**CONFIRMED:** Logout revoked the session.

**CONFIRMED:** Only synthetic authentication and
Mock Banner academic records were used.

**WORKING ASSUMPTION:** The existing Ollama
adapter can support a local live-model Leo demo.

**OPEN QUESTION:** Reliability across different
requests, model failures, multi-turn interactions,
real Entra authentication, and production deployment.

**RECOMMENDATION:** Retain the isolated live probe,
then validate a separate interactive Ollama mode.

Research:
docs/research/2026-11-03-live-ollama-browser-mcp-integration.md

Evidence:
docs/evidence/2026-11-03-step96-live-ollama-observation.md


---

## STEP-103-LEO-EVIDENCE-KEYBOARD-2026-11-03

**CONFIRMED:** Live-model tests demonstrated missing
tool calls for academic history and prerequisites.

**CONFIRMED:** Stronger prompts improved tool
selection but did not guarantee suitable evidence.

**CONFIRMED:** The first deterministic evidence
router caused an existing E17 regression.
The revised implementation restored the
model-first workflow and passed local tests.

**CONFIRMED:** The operator verified corrected
history and prerequisite answers in Microsoft Edge.

**CONFIRMED:** The Friday-restricted scheduling
proposal continued to work.

**CONFIRMED:** The operator verified Enter-to-send.
Shift+Enter newline behavior was added and tested
in the Chromium keyboard regression.

**WORKING ASSUMPTION:** Broader academic requests
can be supported by expanding deterministic
evidence requirements.

**OPEN QUESTION:** Safe rich-text display,
generalized evidence handling, multi-turn context,
and institution-approved integrations.

**RECOMMENDATION:** Preserve existing authentication,
MCP authorization and deterministic validation.
Keep synthetic demo-only login isolated.

Research:
docs/research/2026-11-03-leo-evidence-and-keyboard-validation.md

Evidence:
docs/evidence/2026-11-03-step103-observations.md


---

## STEP-106-LEO-SAFE-FORMATTING-2026-11-03

**CONFIRMED:** Leo's previous text renderer
displayed escaped Markdown characters.

**CONFIRMED:** A limited formatter was added
using fixed DOM elements and text nodes rather
than interpreting model-generated HTML.

**CONFIRMED:** Chromium tested basic bold
formatting, bullet lists, and inert HTML
injection content.

**CONFIRMED:** The authenticated MCP scheduling
and session-revocation checks continued to pass.

**CONFIRMED:** The operator provided live Ollama
output showing improved course-list formatting
and verified synthetic proposal cards.

**CONFIRMED:** No enrollment was performed.

**WORKING ASSUMPTION:** Restricted Markdown
support is sufficient for the current prototype.

**OPEN QUESTION:** Further card-layout polish,
nested lists, rich-text needs and more consistent
model-generated scheduling language.

**RECOMMENDATION:** Continue using safe
DOM-based rendering and keep untrusted model
text separate from verified planner cards.

Research:
docs/research/2026-11-03-leo-safe-response-formatting.md

Observation:
docs/evidence/2026-11-03-step106-formatting-observation.md

Browser screenshot:
docs/evidence/2026-11-03-step104-safe-format-browser.png


---

## STEP-109-LEO-VERIFIED-CARD-READABILITY-2026-11-03

**CONFIRMED:** Leo's verified schedule-card
presentation was improved to separate labels,
values and registration statuses.

**CONFIRMED:** A proposed-only notice was added
to the validated schedule-card interface.

**CONFIRMED:** Chromium verified card readability,
safe formatting, authenticated MCP access,
and session revocation.

**CONFIRMED:** The operator supplied a live Leo
response showing readable card details and
the proposed-only notice.

**CONFIRMED:** The system did not enroll the
synthetic student.

**WORKING ASSUMPTION:** The current layout is
adequate for the next research demonstration.

**OPEN QUESTION:** How to make all model-generated
schedule wording consistently reflect verified
planning evidence rather than imply registration.

**RECOMMENDATION:** Keep planner-derived data
authoritative and continue improving the agent's
evidence-backed language.

Research:
docs/research/2026-11-03-leo-verified-card-readability.md

Observation:
docs/evidence/2026-11-03-step109-card-observations.md

Screenshot:
docs/evidence/2026-11-03-step107-card-layout.png


---

## STEP-112-FOREIGN-RECORD-PRIVACY-2026-11-03

**CONFIRMED:** Step 110 evaluated eight development
cases with live qwen3:4b-instruct. Seven passed.
E15 failed due to academic-record misattribution.

**CONFIRMED:** The E15 failure did not demonstrate
unauthorized retrieval of another student's record.
The model used the authenticated student's data.

**CONFIRMED:** A narrowly scoped privacy guard
was added to refuse recognized requests for
foreign-student academic records before LLM
or MCP access.

**CONFIRMED:** Step 111A passed its targeted and
complete regression tests.

**CONFIRMED:** The corrected E15 evaluation
passed with zero model calls and zero MCP calls.

**WORKING ASSUMPTION:** Additional privacy-intent
patterns may be necessary for broader questions.

**OPEN QUESTION:** How to handle ambiguous and
multi-turn foreign-record requests without
blocking legitimate student planning.

**RECOMMENDATION:** Preserve student-bound MCP
authorization, deterministic evidence checks,
and explicit privacy regression testing.

Research:
docs/research/2026-11-03-leo-foreign-record-privacy-guard.md

Comparison:
docs/evidence/2026-11-03-step112-e15-comparison.json


---

## STEP-115-SESSION-PLAN-CONTEXT-2026-11-03

**CONFIRMED:** The Step 113 audit established
that the gateway and assistant did not preserve
multi-turn conversation context.

**CONFIRMED:** The Step 114 implementation added
a bounded immutable PlanContext data structure
and internal session-bound storage operations.

**CONFIRMED:** Context survives CSRF rotation
and becomes unavailable after session revocation
or expiration.

**CONFIRMED:** Targeted tests and complete
MCP/gateway and AI-agent regression suites passed.

**WORKING ASSUMPTION:** In-memory context storage
is appropriate for isolated synthetic testing,
not production multi-worker deployment.

**OPEN QUESTION:** How should verified planner
results be converted into session context and
applied to subsequent student messages?

**RECOMMENDATION:** Never trust browser-controlled
academic context or previous LLM prose as
authoritative scheduling evidence. Keep identity
and authorization enforced independently by MCP.

**NOT YET IMPLEMENTED:** Context population from
verified planner results, follow-up resolution,
and full multi-turn browser behavior.

Research:
docs/research/2026-11-03-leo-session-plan-context.md


---

## STEP-117-VERIFIED-SESSION-CONTEXT-2026-11-03

**CONFIRMED:** The gateway can now populate
bounded session-specific scheduling context
from successful, validated planner evidence.

**CONFIRMED:** Context projection requires
a grounded completed response, a single
successful plan and matching verified
schedule-card identity, term and sections.

**CONFIRMED:** The browser does not supply
the authoritative planning context.

**CONFIRMED:** Real HTTPS Chromium integration
verified context storage and logout revocation.

**CONFIRMED:** The targeted, complete MCP/gateway
and AI-agent regression suites passed.

**WORKING ASSUMPTION:** In-memory session context
is suitable for synthetic local demonstrations.

**OPEN QUESTION:** How to merge follow-up
preferences safely, preserve the original
student intent and handle concurrent requests.

**RECOMMENDATION:** Implement deterministic
follow-up interpretation with renewed planner
validation. Retain student-scoped MCP
authorization and privacy checks.

**NOT YET IMPLEMENTED:** Automatic reuse of
session context by the conversational agent.

Research:
docs/research/2026-11-03-leo-verified-session-context.md

Evidence:
docs/evidence/2026-11-03-step117-context-verification.md


---

## STEP-120-TWO-TURN-SCHEDULING-2026-11-03

**CONFIRMED:** The authenticated Leo gateway now
supports a narrowly recognized follow-up that
reuses verified session-bound scheduling context.

**CONFIRMED:** The first two-turn browser/MCP test
passed using synthetic student data and a scripted
language model.

**CONFIRMED:** The second turn preserved CIS376,
CIS410 and the mandatory no-Friday preference,
applied a new soft start-time preference, and
executed fresh deterministic schedule validation.

**CONFIRMED:** The test exercised HTTPS, authenticated
MCP access, verified schedule cards, context update
and logout revocation.

**CONFIRMED:** Targeted, complete MCP/gateway and
AI-agent automated test suites passed.

**WORKING ASSUMPTION:** Narrow deterministic follow-up
resolution is appropriate for this research phase.

**OPEN QUESTION:** Whether the same behavior works
reliably with live Ollama across varied wording.

**OPEN QUESTION:** How concurrent requests should
be serialized or rejected to avoid stale updates.

**RECOMMENDATION:** Evaluate live-model two-turn
performance and strengthen multi-turn security
before expanding follow-up functionality.

**LIMITATION:** This is not general conversation
memory, real Entra deployment or live Banner use.

Research:
docs/research/2026-11-03-leo-two-turn-scheduling.md

Evidence:
docs/evidence/2026-11-03-step120-two-turn-validation.md


---

## STEP-126-LIVE-PREFERENCE-CORRECTION-2026-11-03

**CONFIRMED:** A live qwen3:4b-instruct two-turn
evaluation succeeded on its first turn but withheld
verified cards on the second turn after the model
executed two non-equivalent planning calls.

**CONFIRMED:** The live model omitted an
earliest_start value while marking earliest_start
mandatory. The deterministic parser correctly
read the student's wording as soft.

**CONFIRMED:** The missing-value case allowed an
incorrect mandatory flag to survive reconciliation.

**CONFIRMED:** A narrowly scoped final resolver
correction now removes a model's mandatory flag
when the student's relevant wording is reliably
and explicitly soft.

**CONFIRMED:** The existing preference-language
ablation still disables the new correction,
preserving historical evaluation comparisons.

**CONFIRMED:** All Step 126 local regression,
AI-agent, MCP/gateway and scripted Chromium
two-turn tests passed.

**OPEN QUESTION:** The live model's second
planning call dropped CIS410. This independent
course-selection problem remains unresolved.

**OPEN QUESTION:** The corrected code has not
yet passed a new live Ollama two-turn trial.

**RECOMMENDATION:** Preserve the fail-closed
multiple-plan card/context restrictions until
a separately tested consistency policy exists.

**WORKING ASSUMPTION:** Supported English
soft-preference syntax is sufficiently reliable
for this narrow synthetic research scenario.

**LIMITATION:** No real Banner or Entra integration
and no enrollment functionality were tested.

Research:
docs/research/2026-11-03-leo-live-preference-strength-correction.md

Evidence:
docs/evidence/2026-11-03-step126-preference-regression.md

Master SOT v1.2 remains a consolidation draft.


---

## STEP-128-LIVE-TWO-TURN-VALIDATION-2026-11-04

**CONFIRMED:** Live qwen3:4b-instruct completed
a two-turn synthetic course-scheduling conversation
through Chromium HTTPS, the authenticated gateway,
protected MCP tools and the deterministic planner.

**CONFIRMED:** Both CIS376 and CIS410 were preserved
in the second planning operation.

**CONFIRMED:** Friday avoidance remained mandatory.

**CONFIRMED:** The earliest-start preference of
10:01 remained soft despite the model again
supplying an unsupported mandatory flag.

**CONFIRMED:** The second turn had two model calls,
one successful planning operation, and returned
grounded verified schedule cards.

**CONFIRMED:** Verified session context was updated.
The second browser chat returned HTTP 200.

**CONFIRMED:** The existing fail-closed multiple-plan
and context-verification safeguards remain unchanged.

**WORKING ASSUMPTION:** The prototype's narrowly
supported follow-up language provides a useful
starting point for conversational scheduling.

**OPEN QUESTION:** Reliability across repeated
live-model trials and safe treatment of conflicting
or partial planning operations remain unmeasured.

**RECOMMENDATION:** Expand versioned live
evaluation scenarios while preserving all
deterministic eligibility, identity, security
and no-enrollment boundaries.

**LIMITATION:** This was one live-model trial
with synthetic Banner and simulated sign-in,
not a production deployment or success-rate study.

Research:
docs/research/2026-11-04-leo-live-two-turn-success.md

Evidence:
docs/evidence/2026-11-04-step127-live-comparison.json

Master SOT v1.2 remains a consolidation draft.
