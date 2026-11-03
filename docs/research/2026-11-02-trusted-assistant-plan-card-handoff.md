# Trusted Assistant-to-Plan-Card Handoff

Date: 2026-11-02
Workstream: Unified MCP / AI-agent integration
Branch: integration/verified-plan-cards-20261102
Starting commit: 51d93c9

## Objective

Connect deterministic scheduling proposals to Leo's
verified plan-card display contract without exposing
unredacted planner data to the language model.

## CONFIRMED IMPLEMENTATION

Files modified:

- ai-agent/agent/assistant.py
- ai-agent/tests/test_assistant.py
- tests/test_team_mcp_http_integration.py

The SchedulingAssistant now supports an optional
trusted plan_card_projector callback.

Verified planning results are projected separately
from the existing redacted model-facing tool response.

Projected cards are stored in request-scoped state
and may be included in AssistantResult.plan_cards.

The existing tool-output redaction remains intact.

## SECURITY AND FAILURE HANDLING

- No student identity is accepted from model arguments.
- The application must supply a trusted projector.
- Plan cards remain proposed_only.
- Cards are suppressed after unverified answers.
- Cards are suppressed after ambiguous multiple
  planning attempts.
- Cards are suppressed when evidence is missing.
- Cards are suppressed for system fallback responses.
- Projection failures do not interrupt successful
  scheduling answers.
- Projector exception details are not returned.
- The protected MCP server remains read-only.

## CONFIRMED TEST EVIDENCE

Step 46:
- Authenticated HTTP integration: 1 passed.
- Plan-card contract tests: 23 passed.

Step 47:
- MCP suite: 128 passed.
- AI-agent suite: 1036 passed, 1 skipped.

Step 48:
- Targeted MCP/plan-card tests: 24 passed.
- Targeted assistant tests: 19 passed, 1 skipped.

Step 49:
- Complete MCP suite: 128 passed.
- Complete AI-agent suite: 1040 passed, 1 skipped.

Step 49 evidence files:

- docs/evidence/2026-11-02-step49-mcp-regression.txt
- docs/evidence/2026-11-02-step49-agent-regression.txt

These are locally observed synthetic research tests.

## WORKING ASSUMPTION

The trusted browser gateway will construct the
projector using server-verified student identity
and term context.

## OPEN QUESTIONS

- Browser gateway implementation and authentication.
- Actual Leo UI integration.
- End-to-end browser testing.
- Authorized course-title and credit enrichment.
- Production Entra identity mapping.
- University-approved Banner integration.
- Final consolidated master SOT reconciliation.

## RECOMMENDATION

Review the complete integration diff, then merge
through a tested pull request.

Keep the master SOT v1.2 document classified as
a consolidation draft until reconciliation is
completed and verified.

Do not claim production readiness from these tests.
