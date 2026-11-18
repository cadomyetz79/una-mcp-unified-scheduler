# Local HTTPS Leo Browser-to-MCP Validation

Date: 2026-11-03
Project: UNA MCP AI Scheduling Research Project
Workstream: Browser UI / Authentication / MCP Integration
Branch: integration/browser-gateway-20261102
Starting commit: dd115e1

## Objective

Verify that a real Chromium browser can communicate
with a running HTTPS FastAPI gateway, complete an
isolated synthetic OAuth callback, and display results
produced by the protected MCP scheduling pipeline.

## CONFIRMED — Environment

The test used:
- Headless Chromium via Playwright
- FastAPI served by Uvicorn
- A temporary self-signed HTTPS certificate
- A gateway bound only to 127.0.0.1
- Synthetic OAuth authorization-code exchange
- Locally signed test JWT
- An in-process protected MCP ASGI server
- Existing deterministic scheduling implementation
- Scripted AI tool selection
- Synthetic Mock Banner responses

## CONFIRMED — Implementation

Added:
scripts/leo_local_https_demo.py

Captured screenshot:
docs/evidence/2026-11-02-step88-live-browser-mcp.png

The test's Python import path was made
self-contained for reproducibility.

The default gateway was not modified to permit
development login or synthetic token issuance.

## CONFIRMED — Browser Observations

- Local HTTPS endpoint returned HTTP 200.
- Leo's HTML, CSS, JavaScript and lion logo loaded.
- Unauthenticated session status returned HTTP 401.
- The actual OAuth login route generated a redirect.
- The test inspected the OAuth URL without following
  the external Microsoft authorization endpoint.
- The test simulated approval with a research-only code.
- Chromium loaded the actual local HTTPS callback.
- The server issued an authenticated session.
- The browser loaded the signed-in Leo interface.
- The browser submitted a real HTTPS chat request.
- Protected MCP tools executed the scheduling workflow.
- The UI displayed two verified synthetic sections.
- Logout succeeded and revoked the session.
- Session status subsequently returned HTTP 401.
- No uncaught JavaScript errors failed the test.

## CONFIRMED — Academic Result

Student: S10001
Term: 2027SP

Verified schedule proposal included:
- SEC1001
- SEC2002

The result was proposal-only.

No enrollment, registration or academic record
modification was performed.

## CONFIRMED — Problems Encountered

1. Direct execution initially failed because Python
   could not resolve the repository's src package.

   Fix: include the repository root in the test's
   module import path.

2. Initial navigation timed out while waiting for
   networkidle.

   Fix: use document readiness assertions and add
   an independent HTTPS connectivity diagnostic.

3. The first identity-provider interception allowed
   unexpected navigation toward Microsoft. A handler
   then received a URL without the expected client_id
   query parameter.

   Fix: obtain the authorization URL directly from
   the local gateway without following the external
   redirect. Simulate provider approval inside the
   test, then navigate Chromium to the real local
   callback endpoint.

The corrected final demonstration passed.

Browser request-aborted diagnostics were observed
during navigation/logout, but the test completed
and verified session revocation.

## CONFIRMED — Test Results

Local browser-to-HTTPS-MCP test: passed.

Complete MCP suite:
206 passed.

AI-agent suite:
1044 passed, 1 skipped.

Evidence:
docs/evidence/2026-11-03-step89-https-browser-mcp.txt
docs/evidence/2026-11-03-step89-mcp-regression.txt
docs/evidence/2026-11-03-step89-agent-regression.txt

## SECURITY AND LIMITATIONS

The browser contacted an actual local HTTPS gateway.

The identity provider was simulated. The final
successful test did not navigate to Microsoft's
authorization endpoint.

The server used a temporary self-signed certificate.
The browser test explicitly accepted that certificate.

The protected MCP implementation and real scheduling
handlers executed through an in-process ASGI transport,
not a separately deployed MCP network service.

The LLM was scripted.

No real Entra credentials, institutional records,
or live Banner service were involved.

The session store remains a research implementation.

This is not proof of production deployment security.

## WORKING ASSUMPTION

This integrated architecture is suitable as the
foundation for a controlled synthetic demonstration.

## OPEN QUESTIONS

- Approved Microsoft Entra login
- University-authorized identity configuration
- Production TLS and reverse proxy configuration
- Persistent session storage
- Separately deployed MCP service
- Live LLM validation
- RAG and OCR integration
- Final master SOT reconciliation

## RECOMMENDATION

Preserve this browser integration test as a research
baseline.

Next, create a controlled manual demonstration
environment where a developer can interact with Leo
in a visible browser using synthetic accounts.

Do not enable production authentication or real
student information without institutional approval.

Master SOT v1.2 remains a consolidation draft.


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
