# Signed Browser Session to Protected MCP Integration

Date: 2026-11-02
Project: UNA MCP AI Scheduling Research Project
Workstream: Unified gateway / security / MCP integration
Starting commit: cbeed8d
Branch: integration/browser-gateway-20261102

## Objective

Demonstrate that the unified scheduling system can
authenticate a synthetic browser session, execute
protected MCP scheduling operations, and return
verified student-specific schedule proposals.

## CONFIRMED — Implementation

Added:
tests/test_gateway_full_browser_mcp.py

The integration test executes:

1. Locally signed Entra-compatible synthetic JWT
2. Cryptographic JWT verification
3. Server-side authenticated browser session creation
4. HTTPS session bootstrap and CSRF rotation
5. CSRF-protected scheduling HTTP request
6. Gateway identity revalidation
7. AuthenticatedSchedulingRunner
8. Protected MCP tool handlers
9. Synthetic academic backend
10. Deterministic schedule planner
11. Verified Leo schedule-card projection
12. Logout and session revocation

The test reuses existing protected MCP handlers
and the authenticated scheduling runner.

The scripted LLM selects the planning tool.
The actual MCP authorization and deterministic
planning components execute.

## CONFIRMED — Positive Result

Authorized synthetic student: S10001
Term: 2027SP

Returned verified proposal:
- SEC1001
- SEC2002

Card schema: leo-team-plan-v1
Card status: proposed_only

The response contains no enrollment confirmation.

## CONFIRMED — Negative Security Cases

The test verifies rejection of:

- Unmapped student identity
- Incorrect JWT audience
- Missing academic.read scope
- Missing CSRF token
- Stale CSRF token
- Cross-origin request
- Client-supplied conflicting student ID
- Competing bearer and session credentials
- Session reuse following logout

Rejected browser requests do not invoke the
authenticated scheduling runner.

Responses exclude bearer credentials, session
secrets, internal MCP traces and security metadata.

## CONFIRMED — Test Evidence

Step 75:
- New end-to-end integration: 1 passed
- Combined integration tests: 5 passed
- Complete MCP suite: 175 passed

Step 76:
- End-to-end regression evidence:
  docs/evidence/2026-11-02-step76-full-integration.txt

- Complete MCP regression evidence:
  docs/evidence/2026-11-02-step76-mcp-regression.txt

- Complete AI-agent regression evidence:
  docs/evidence/2026-11-02-step76-agent-regression.txt

## LIMITATIONS

No real Microsoft Entra sign-in took place.

A trusted test harness issued the session after
verifying a locally signed synthetic JWT.

The LLM was scripted rather than using a live
OpenAI model.

The HTTP integration did not execute the
frontend JavaScript in a graphical browser.

No real UNA student data or Banner connection
was used.

The default application still has no approved
browser login callback or session issuer.

The in-memory session store is a prototype
component, not production session infrastructure.

## WORKING ASSUMPTION

The verified backend workflow can support Leo's
existing interactive interface once approved
authentication and browser-level testing are
completed.

## OPEN QUESTIONS

- Approved Entra authorization-code sign-in
- End-to-end graphical browser validation
- Live OpenAI agent demonstration
- Browser session deployment over HTTPS
- RAG and OCR orchestration
- Final master SOT consolidation

## RECOMMENDATION

Preserve the original Leo UI and lion branding.

Keep real identity integration separate from
synthetic authentication used in tests.

Continue enforcing academic authorization at
both the gateway and MCP service boundaries.

Retain deterministic schedule verification,
student-specific plan cards and proposal-only
semantics.

Master SOT v1.2 remains a consolidation draft.
