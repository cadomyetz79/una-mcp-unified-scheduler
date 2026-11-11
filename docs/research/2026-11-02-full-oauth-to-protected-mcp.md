# Full Synthetic OAuth-to-Protected-MCP Integration

Date: 2026-11-02
Project: UNA MCP AI Scheduling Research Project
Workstream: Authentication / Gateway / MCP / AI Agent
Branch: integration/browser-gateway-20261102
Starting commit: 752cb90

## Objective

Verify the full synthetic OAuth login through
protected MCP scheduling and verified Leo schedule
cards in one integrated application test.

## CONFIRMED — Implementation

Added:
tests/test_gateway_oauth_mcp_integration.py

The test constructs an isolated FastAPI gateway,
OAuth state store, server-side browser session store,
and real protected MCP server with six existing
academic tool handlers.

The test injects a fake authorization-code exchanger
and uses a locally generated RSA signing key.

A scripted LLM selects the plan_schedule operation.

The actual MCP authorization, academic tool handlers,
deterministic scheduling logic, and verified plan-card
projection execute.

## CONFIRMED — Tested Workflow

1. Anonymous browser session is denied.
2. Synthetic OAuth login starts.
3. PKCE S256 challenge and state are generated.
4. OAuth callback receives the matching state.
5. Fake exchanger validates the expected PKCE
   challenge and returns a locally signed JWT.
6. JWT signature and required identity claims
   are verified.
7. Authorized student S10001 receives an opaque,
   server-side browser session.
8. Leo's session status endpoint verifies identity
   and supplies a CSRF token.
9. Invalid browser requests are rejected.
10. The gateway invokes the scheduling runner.
11. The runner calls the protected MCP server.
12. The deterministic planner produces a proposal.
13. Verified student-specific Leo cards are returned.
14. Logout revokes the browser session.
15. Replaying the OAuth callback is rejected.

## CONFIRMED — Academic Result

Student: S10001
Term: 2027SP
Schema: leo-team-plan-v1
Status: proposed_only

Returned sections:
- SEC1001
- SEC2002

Total proposed credits in the scripted response: 6.

No enrollment, registration, or course assignment
was performed.

## CONFIRMED — Security Observations

The test verified:

- Anonymous session rejection
- Missing CSRF token rejection
- Cross-origin request rejection
- Browser-supplied student identity rejection
- Student-specific scheduling context
- Non-disclosure of the delegated bearer token
- No internal MCP trace in the browser response
- Session revocation following logout
- One-time OAuth state consumption

Earlier independent tests also cover incorrect
signatures, unmapped identities, OAuth correlation
errors, and expired states.

## CONFIRMED — Test Results

Step 86:
- End-to-end OAuth-to-MCP test: 1 passed
- Related integration tests: 13 passed
- Complete MCP suite: 206 passed
- AI-agent suite: 1044 passed, 1 skipped

Step 87 evidence:
docs/evidence/2026-11-02-step87-oauth-mcp-integration.txt
docs/evidence/2026-11-02-step87-mcp-regression.txt
docs/evidence/2026-11-02-step87-agent-regression.txt

## LIMITATIONS

No real Microsoft Entra authorization endpoint or
token exchange was contacted.

The authorization-code exchanger is a test fixture,
not an approved production MSAL integration.

The JWT was locally signed for synthetic testing.

The LLM was scripted rather than a live model.

The integration uses an HTTP client test harness,
not a graphical browser running against a deployed
HTTPS gateway and MCP service.

The session store is an in-process research prototype.

No actual UNA student records or live Banner data
were accessed.

## WORKING ASSUMPTION

The tested gateway components provide a viable
foundation for a future university-approved,
authenticated Leo demonstration.

## OPEN QUESTIONS

- Approved Microsoft Entra app registration
- Confidential server-side code exchange
- Actual HTTPS deployment and reverse proxy
- Multi-worker session persistence and revocation
- Full graphical browser login-to-MCP execution
- Live LLM integration
- RAG and OCR integration
- University IT/security authorization

## RECOMMENDATION

Preserve this test as a regression baseline.

Do not enable real institutional authentication
until approved configuration, session management,
deployment controls, and security review exist.

Keep the draft pull request open until GitHub CI
passes on this milestone commit.

The master SOT v1.2 remains a consolidation draft.
