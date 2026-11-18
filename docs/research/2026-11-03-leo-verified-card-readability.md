# Leo Verified Schedule Card Readability

Date: 2026-11-03
Starting commit: 5d1d605

## Objective

Improve the clarity of verified synthetic
schedule proposals in Leo's browser UI.

## CONFIRMED — Implementation

Changed:

- src/gateway/leo_ui/unified.js
- src/gateway/leo_ui/interactive.css
- scripts/leo_local_https_demo.py

The UI now presents:

- Clearer field labels
- More readable registration statuses
- Responsive card spacing
- A prominent proposed-only notice

The notice derives from the validated
proposed-only schedule-card contract,
not from unrestricted model-generated text.

## CONFIRMED — Validation

The Chromium browser test passed its
card-readability assertions.

It also verified the existing protected
MCP scheduling and browser security flow.

The operator provided a live Leo response
showing the proposal notice and readable
synthetic registration details.

The MCP and AI-agent regression suites
were rerun before committing.

## Security implications

No changes were made to:

- Authentication or CSRF enforcement
- Student-scoped authorization
- MCP academic tools
- Deterministic schedule validation
- Enrollment capabilities

Untrusted model content remains subject
to the restricted safe-text formatter.

## WORKING ASSUMPTION

The revised schedule cards are suitable
for current research demonstrations.

## OPEN QUESTIONS

- Consistent model wording for proposals
- Wider language and academic question coverage
- Multi-turn conversational context
- Additional accessibility and mobile testing
- Production identity/data integration

## RECOMMENDATION

Make verified planner data authoritative
for any claim about schedule validity,
eligibility or registration status.

Continue distinguishing proposed plans
from completed enrollment actions.
