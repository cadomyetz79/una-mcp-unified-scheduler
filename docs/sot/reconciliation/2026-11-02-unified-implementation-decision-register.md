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


---

## STEP-130-LIVE-REPEATABILITY-2026-11-04

**CONFIRMED:** Three separate live Ollama
two-turn synthetic scheduling trials passed.

**CONFIRMED:** The model was qwen3:4b-instruct
with temperature set to zero.

**CONFIRMED:** All three second turns preserved
CIS376 and CIS410, mandatory Friday avoidance,
and the soft earliest-start preference of 10:01.

**CONFIRMED:** Each second turn executed one
successful planning operation and returned
grounded verified schedule cards.

**CONFIRMED:** Session context updates and
session revocation succeeded in all three trials.

**CONFIRMED:** Observed success was 3/3 (100%)
for the specified repeated synthetic scenario.

**WORKING ASSUMPTION:** Narrow conversational
follow-up support is repeatable for the tested
synthetic request pattern.

**OPEN QUESTION:** Performance across other
requests, larger evaluation sets, concurrency,
and production infrastructure remains unknown.

**RECOMMENDATION:** Expand scenario coverage
before calculating broader reliability estimates.

**LIMITATION:** The result is three executions
of one synthetic scenario, not a production
success-rate or readiness claim.

Research:
docs/research/2026-11-04-leo-live-repeatability.md

Evidence:
docs/evidence/2026-11-04-step129-three-trial-repeatability.json

Master SOT v1.2 remains a consolidation draft.


---

## STEP-133B-WEEKDAY-CONTINUITY-2026-11-04

**CONFIRMED:** The supported Wednesday follow-up reconstructs both requested
courses and preserves mandatory Friday and Wednesday avoidance, plus unchanged
time values and strengths. Continuation cards and context replacement are rejected
when verified planner inputs fail the continuity comparison.

**CONFIRMED:** Explicit reset candidates must match the new courses and term.
Unsupported edits and mixed soft/mandatory day avoidance fail closed; equivalent
day ordering is accepted. Authorization, privacy, multiple-plan verification,
and no-enrollment safeguards are retained.

**CONFIRMED:** Corrected live Chromium/Ollama qwen3:4b-instruct trial passed all
three turns and logout. The Wednesday turn used two model calls and one successful
planner call, returned HTTP 200, and saved WED/FRI as mandatory with 10:01 soft.
Both CIS376 and CIS410 remained in requested context. The proposal was partial:
CIS410/SEC2002 only; CIS376 was explicitly excluded because no open section met
the mandatory days. Existing registrations were not changed.

**CONFIRMED:** Final tests: 26 focused continuity cases; 281 MCP/gateway tests;
1,073 AI-agent tests passed and 1 skipped. Focused cases are included in 281.

**CONFIRMED:** Live trial 1 is retained as failed: its probe incorrectly expected
zero options instead of the supported partial proposal. Trial 2 corrected that
expectation and verified section days, exclusion, browser explanation, context,
and revocation. Do not characterize these as two passing trials.

**WORKING ASSUMPTIONS:** Narrow verified reconstruction supports the tested
synthetic grammar; retaining all requested courses across partial proposals is
the intended continuity contract. Larger-scale reliability is unmeasured.

**OPEN QUESTIONS:** Broader wording and course edits; mixed day strengths;
concurrent updates; intent persistence after no verified proposal; deterministic
partial-plan exclusion labels; production identity/data integration.

**RECOMMENDATIONS:** Keep existing safeguards. Design versioned intent updates
and explicit partial-plan exclusions before expanding scope. Run larger independent
evaluations before reliability or production-readiness claims.

Research:
docs/research/2026-11-04-leo-weekday-continuity.md

Evidence:
docs/evidence/2026-11-04-step133-live-continuity-trial1.json
docs/evidence/2026-11-04-step133-live-continuity-trial2.json
docs/evidence/2026-11-04-step133-validation-metadata.json

Master SOT v1.2 remains a consolidation draft. PR #3 remains draft.


---

## STEP-134-CONTEXT-CONCURRENCY-2026-11-04

**CONFIRMED:** Server-side context revisions now prevent stale in-flight results
from overwriting a newer verified plan or returning stale model prose. Snapshot
read and conditional commit are atomic within the single-process store. Clear
operations advance revisions, CSRF rotation preserves them, and revisions are
not accepted from browser/model input.

**CONFIRMED:** Stale finalization returns HTTP 409; logout/expiry returns HTTP 401,
including cardless replies. The browser preserves the user's message for review
and manual retry. A two-thread regression confirms exactly one commit succeeds
from a shared revision.

**CONFIRMED:** Initial regressions: 8 failed, 2 passed. Final results: 18 focused
concurrency cases; 299 MCP/gateway passed; 1,073 AI-agent passed, 1 skipped.
Focused cases are included in 299. Chromium conflict/retry, logout, wrong-student,
and mobile checks passed.

**CONFIRMED:** One sequential live Chromium/Ollama qwen3:4b-instruct trial passed
all three turns and logout after the revision guard. Wednesday and Friday remained
mandatory, 10:01 remained soft, and both requested courses remained in context.
The partial proposal remained CIS410 only, with CIS376 explicitly excluded.
This is not a live concurrent-model benchmark.

**CONFIRMED:** Evidence output now uses a unique matching JSON/PNG basename and
rejects existing artifacts; the overwrite guard was tested and Step 133 evidence
preserved. Security guards and the no-enrollment boundary remain unchanged.

**WORKING ASSUMPTIONS:** First verified completion wins, with review/retry for
stale results, is an appropriate local prototype policy; usability is unmeasured.

**OPEN QUESTIONS:** Multi-worker atomic storage/revocation; cross-tab display
synchronization; durable unsatisfied intent; cancelling unnecessary model work;
partial-plan labels; broader wording; production identity/data integration.

**RECOMMENDATIONS:** Carry revision checks into any future durable intent model.
Use shared transactional storage before multi-worker deployment. Implement
deterministic partial-plan exclusion labels as the next bounded phase.

Research:
docs/research/2026-11-04-leo-context-concurrency.md

Evidence:
docs/evidence/2026-11-04-step134-validation-metadata.json
docs/evidence/2026-11-04-step134-live-continuity-trial1.json

Master SOT v1.2 remains a consolidation draft. PR #3 remains draft.

---

## STEP-135A-PROFESSOR-ENTRA-RAG-AUTHORIZATION-2026-11-05

**Source:** Professor's 15-page *Entra_ID_MCP_RAG_Authorization_Student_Handout.docx* (received 2026-11-05); research analysis in `docs/research/2026-11-05-entra-rag-authorization-phase135.md`.

**CONFIRMED:** The handout specifies role/group authorization for MCP operations, document ACL assignment before chunking, metadata filtering before vector ranking, and post-retrieval verification before LLM context construction. It uses synthetic Entra identities and a backend-independent PostgreSQL/pgvector teaching example.

**CONFIRMED:** Existing protected academic MCP checks bind synthetic student identity and academic.read, but existing RAGFlow public/synthetic adapter does not enforce role/group document ACL or per-chunk post-verification. The sample handout tool policy contains a role/group OR-default logic hazard; do not copy it unchanged.

**CONFIRMED:** Added isolated, pure `src/mcp_server/entra_rbac_acl.py` and `tests/test_entra_rbac_acl.py`, commits `67ee466` and `9b40c7d`. The module models trusted role/group/scope context, server-owned tool policies, document ACL hashes and versions, allowed-document candidate filtering and independent chunk revalidation. The Student/Faculty/HR/Finance/Legal teaching matrix and negative synthetic cases are exercised. Seven GitHub checks completed successfully at the test commit, including four pytest platforms, browser CI and existing integration checks.

**CONFIRMED limitation:** This new contract is **not wired to protected MCP or RAGFlow**. No role-based live tool authorization, actual document ACL ingestion, real vector metadata filtering, PostgreSQL migration, Graph group-overage resolution, audit pipeline or Entra production tenant is claimed.

**WORKING ASSUMPTION:** Reusing one trusted authorization context across MCP and retrieval is appropriate if the server alone controls its creation, authorizer policies, and dataset ACL. RAGFlow filter payloads must be matched against the installed backend/API version.

**OPEN QUESTION:** Current RAGFlow metadata/index backend, authoritative document classification policy, approved Entra role/group IDs, Graph group overage, exact integration contracts, and five-identity end-to-end results.

**RECOMMENDATION:** Follow gates 135B–135E in the dated research note. Keep role/security attributes out of LLM tool arguments; reject all unsupported protected retrieval. No live student/HR/Finance/Legal records and no enrollment writes.

**Master status:** Consolidated Markdown v1.3 receives this supplemental phase; Word v1.3 remains a historical export until a later full-document regeneration and team review.


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
