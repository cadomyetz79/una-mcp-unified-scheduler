# Leo — First Verified Two-Turn Scheduling Conversation

Date: 2026-11-03
Starting checkpoint: 39d50a3

## Research objective

Demonstrate that one authenticated student can
refine an earlier schedule through a subsequent
conversational message without repeating courses
or abandoning previously verified restrictions.

## CONFIRMED — Architecture

The authenticated browser gateway continues to
accept only the current student question.

After authentication and CSRF verification,
the gateway retrieves the bounded PlanContext
associated with the trusted browser session.

Only narrowly recognized follow-up wording
is resolved into a new complete scheduling
request. Unrecognized wording is passed through
to the existing agent unchanged.

The reconstructed request is processed through
the existing authenticated MCP tool interface
and deterministic academic planner.

No previous AI-generated prose is treated
as authoritative academic data.

## CONFIRMED — Implementation files

Modified:
- src/gateway/plan_context.py
- src/gateway/session_routes.py
- scripts/leo_local_https_demo.py

Added:
- tests/test_gateway_followup_resolution.py
- tests/test_gateway_multi_turn_routes.py

## CONFIRMED — Demonstrated scenario

First message:
Plan CIS376 and CIS410 for 2027SP, but
I cannot have classes on Fridays.

Second message:
Actually, I'd prefer classes that start
after 10 AM. Keep everything else the same.

The second request reused course identifiers
CIS376 and CIS410, retained the mandatory
Friday restriction, and introduced a soft
earliest-start preference of 10:01.

The one-minute adjustment reflects the
prototype's interpretation of "after 10"
as strictly later than 10:00.

The deterministic planner ran again using
the authenticated student's synthetic data.

The verified session context was updated
from the new planning operation.

## CONFIRMED — Security properties tested

- Authentication remains server-side
- CSRF and HTTPS origin checks remain active
- Browser requests cannot select another session
- Student identity remains server-derived
- Rejected or unknown follow-ups are not rewritten
- Previous mandatory start limits are not weakened
- The revised plan is validated again
- Logout invalidates the session context
- No enrollment operation is performed

## CONFIRMED — Testing

Step 119B passed:

- 52 targeted tests
- 255 MCP/gateway tests
- 1064 AI-agent tests
- 1 AI-agent test skipped

The real HTTPS Chromium integration passed
its two-turn context and planner assertions.

Step 120 reran these checks before commit.

See:
docs/evidence/2026-11-03-step120-two-turn-validation.md

## WORKING ASSUMPTION

Narrow, deterministic follow-up resolution
is a suitable first research milestone.

The existing in-process session store remains
suitable only for isolated synthetic testing.

## OPEN QUESTIONS

- Broader follow-up language
- Changing or removing earlier preferences
- Course additions, removals and section switches
- Multi-turn privacy-intent coverage
- Concurrent requests and stale context updates
- Live Ollama two-turn success rate
- Multi-worker storage and deployment
- More general conversation state management

## RECOMMENDATION

Evaluate the demonstrated workflow with a
live local language model before expanding
the natural-language follow-up surface.

Preserve existing MCP authorization,
privacy refusal, deterministic planning,
evidence checks and no-enrollment guarantees.

## Important distinction

This milestone proves a working two-turn
synthetic integration using a scripted model.

It does not yet prove unrestricted
conversational memory or production readiness.
