# Opt-in OAuth Callback Integration

Date: 2026-11-02
Project: UNA MCP AI Scheduling Research Project
Workstream: Browser authentication and security
Branch: integration/browser-gateway-20261102
Starting commit: 3deefd4

## Objective

Connect the existing OAuth PKCE/state foundation to
the unified gateway's authenticated browser-session
architecture.

The implementation must remain opt-in and must not
activate real university sign-in.

## CONFIRMED — Implementation

Added:
- src/gateway/oauth_routes.py
- tests/test_gateway_oauth_routes.py

Updated:
- src/gateway/session_routes.py

The OAuth route installer requires an existing
trusted browser-session configuration.

It reuses that configuration's:
- HTTPS origin
- Session store
- JWT verifier
- Student identity mapping
- Allowed issuer

The opt-in endpoints are:
- GET /auth/login
- GET /auth/callback

A successful synthetic callback redirects the
browser to /leo/session.

## CONFIRMED — Security Design

OAuth login requests use a random, short-lived,
browser-correlated state and PKCE S256 challenge.

Callback processing requires:
1. The configured HTTPS origin
2. A valid browser correlation cookie
3. A matching, one-time OAuth state
4. A trusted authorization-code exchange adapter
5. A cryptographically verified delegated JWT
6. An authorized synthetic student mapping
7. Server-side creation of an opaque session

The browser session cookie is Secure, HttpOnly
and SameSite=Strict.

The code does not implement a Microsoft token
exchange or configure an approved Entra client.

The test exchanger is injected only into isolated
synthetic test application instances.

The default gateway does not install these routes.

## CONFIRMED — Initial Test Failure

The initial Step 84 test run reported:
- 9 passed
- 1 failed

The failed assertion expected that a callback
from an unrelated browser, without a correlation
cookie, would consume another browser's pending
OAuth state.

Observed behavior:
- Browser B's invalid callback returned HTTP 401.
- Browser A retained its valid pending state.
- Browser A's subsequent valid callback returned
  HTTP 303.

This was an incorrect test expectation, not
evidence of an authentication bypass.

## CONFIRMED — Correction and Additional Test

Step 84A updated the original test to verify that
a missing-cookie callback is rejected while the
legitimate browser can complete its pending flow.

An additional test verifies that a well-formed
but incorrect correlation cookie consumes the
matching pending state, preventing subsequent
replay.

The new tests cover:
- Successful signed-token callback
- Correct PKCE verifier handoff
- Secure session-cookie issuance
- OAuth state replay rejection
- Missing browser correlation cookie
- Incorrect browser correlation cookie
- Invalid token signatures
- Unmapped student identities
- Invalid callback parameters
- HTTPS and host restrictions
- No OAuth endpoints in the default gateway

## CONFIRMED — Test Evidence

Step 84A:
- OAuth callback tests: 11 passed
- Combined authentication tests: 62 passed
- Complete MCP suite: 205 passed
- AI-agent suite: 1044 passed, 1 skipped

Step 85 evidence:
- docs/evidence/2026-11-02-step85-oauth-callback.txt
- docs/evidence/2026-11-02-step85-auth-security.txt
- docs/evidence/2026-11-02-step85-mcp-regression.txt
- docs/evidence/2026-11-02-step85-agent-regression.txt

## LIMITATIONS

No actual Microsoft authorization-code exchange
was performed.

The synthetic exchange adapter does not establish
production-ready Microsoft PKCE validation.

No real Entra login was activated.

The browser/session infrastructure remains
research-only and in-memory.

Real university identity mappings and student
records were not accessed.

No enrollment was performed.

## WORKING ASSUMPTION

The opt-in route contract can support a future
approved confidential Entra integration following
additional security review.

## OPEN QUESTIONS

- Approved Microsoft Entra app registration
- Confidential MSAL code-exchange implementation
- HTTPS deployment and reverse-proxy trust
- Production session storage
- Complete login-to-protected-MCP integration
- Final live browser authentication tests
- RAG and OCR integration
- Final master SOT reconciliation

## RECOMMENDATION

Next test the complete synthetic OAuth callback
through the real protected MCP scheduling planner.

Do not deploy OAuth routes or accept real student
tokens until institutional approval and
production security review are complete.

Master SOT v1.2 remains a consolidation draft.
