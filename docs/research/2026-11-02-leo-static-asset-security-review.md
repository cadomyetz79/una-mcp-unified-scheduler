# Leo Static Asset Security Review

Date: 2026-11-02
Branch: integration/browser-gateway-20261102
Starting commit: e9ed91d
Workstream: Browser gateway security

## Objective

Prevent static URLs from exposing unintended
original or interactive HTML research documents
while preserving the approved Leo interface.

## CONFIRMED — Implementation

Changed:
- src/gateway/app.py
- tests/test_gateway_frontend.py

Added:
- tests/test_gateway_leo_asset_policy.py

The /leo-assets endpoint now uses an explicit
allowlist of public CSS, JavaScript and logo assets.

Original source assets remain in the Git repository.

The visual homepage remains available at /.

The interactive page remains available at
/leo/session only when the opt-in browser session
routes are installed.

## CONFIRMED — Security

Direct static requests for preview.html,
interactive.html and session.html are rejected.

Unused original JavaScript and historical lion
assets are also excluded from public serving.

The selected lion-only PNG remains unchanged.

No authentication bypass or new login flow
was introduced.

## CONFIRMED — Test Evidence

Step 78 results:

docs/evidence/2026-11-02-step78-mcp-regression.txt

docs/evidence/2026-11-02-step78-agent-regression.txt

## LIMITATIONS

This is a static asset exposure control, not
a complete browser security assessment.

An opt-in interactive page can still be fetched
without authentication, but academic API
operations remain session-protected.

No university-approved OAuth login is configured.

Real-browser interaction remains unverified.

## RECOMMENDATION

Keep the allowlist restricted to files actually
needed by the approved Leo UI.

Review GitHub CI for the updated commit
before merging the draft pull request.

Master SOT v1.2 remains a consolidation draft.
