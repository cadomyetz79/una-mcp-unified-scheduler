# Authenticated Browser Gateway and MCP Integration

Date: 2026-11-02
Project: UNA MCP AI Scheduling Research Project
Phase: Browser gateway foundation and authenticated integration
Workstream: Unified MCP / AI-agent integration
Branch: integration/browser-gateway-20261102
Starting commit: 77c21cc

## Objective

Create the first trusted HTTP interface between a future
student-facing browser application and the unified
AI scheduling system.

Reuse the existing protected MCP tools and deterministic
scheduling planner rather than duplicating academic logic.

## CONFIRMED — Implementation

Added:

- src/gateway/__init__.py
- src/gateway/app.py
- src/gateway/runner.py
- tests/test_browser_gateway.py
- tests/test_gateway_mcp_agent_integration.py

The gateway exposes:

- GET /health
- POST /api/chat

Chat requests accept a question but do not accept a
browser-selected student ID.

The gateway verifies the bearer token, resolves the
authorized student through server-side identity mapping,
and invokes the configured assistant runner.

The runner connects to the protected MCP service using
authenticated streamable HTTP.

It constructs SchedulingAssistant with the existing
BannerTools implementation and trusted plan-card projector.

Responses contain the conversational answer and optional
verified plan_cards, not internal agent traces.

## CONFIRMED — Security Boundaries

The tested gateway rejects:

- Missing authentication
- Invalid bearer tokens
- Incorrect token audiences
- Insufficient academic permissions
- Unmapped student identities
- Browser-supplied student identity fields

An authenticated runner invocation requesting another
student's records was also tested. The protected MCP
authorization boundary prevented successful planning.

The gateway does not expose enrollment operations.

Plan cards remain proposed_only.

Academic API responses include Cache-Control: no-store.

## CONFIRMED — Test Evidence

Step 60:
- Gateway contract tests: 8 passed
- Complete MCP suite: 136 passed

Step 61:
- Signed gateway/MCP/agent integration: 1 passed
- Gateway test set: 9 passed
- Complete MCP suite: 137 passed

Step 62:
- Signed security integration: 1 passed
- Gateway test set: 9 passed
- Complete MCP suite: 137 passed
- Complete AI-agent suite: 1044 passed, 1 skipped

Final evidence files:

docs/evidence/2026-11-02-step62-mcp-regression.txt

docs/evidence/2026-11-02-step62-agent-regression.txt

The end-to-end integration uses synthetic signed JWTs,
temporary test keys, mocked academic data and ScriptedLLM.

No real university student data or university credentials
were involved.

## CONFIRMED — Deployment Limitation

The default gateway application has no assistant runner
configured and fails closed for academic chat.

A successful isolated integration test does not establish
that a live production gateway is deployed.

## WORKING ASSUMPTION

The final application will use an institutionally approved
authentication flow and server-side identity mapping.

The gateway will supply trusted identity and term context
to the existing AI assistant.

## OPEN QUESTIONS

- Actual browser frontend implementation
- Live LLM configuration and browser demonstration
- Approved Entra login architecture
- Real university identity-to-student mapping
- Session/token handling in the browser
- Frontend security and end-to-end browser tests
- RAG and OCR integration with the gateway
- University-approved Banner integration
- Final master SOT reconciliation

## RECOMMENDATION

Keep the current gateway fail-closed until its real
assistant runner is explicitly configured.

Use synthetic identities and data for development.

Review and promote through a pull request with CI.

Do not represent this phase as production deployment.
