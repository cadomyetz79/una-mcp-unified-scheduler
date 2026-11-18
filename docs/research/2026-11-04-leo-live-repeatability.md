# Leo — Live Two-Turn Repeatability Evaluation

Date: 2026-11-04
Starting commit: 2016002

## Research objective

Evaluate whether the corrected Leo prototype
repeatedly completes the same two-turn synthetic
scheduling conversation with live Ollama.

## CONFIRMED — Test environment

- Ollama model: qwen3:4b-instruct
- Temperature: 0.0
- Three separate execution trials
- Fresh Chromium HTTPS browser workflow per trial
- Synthetic OAuth approval and authenticated session
- Protected MCP academic tools
- Mock Banner student and course data
- Deterministic scheduling planner

## CONFIRMED — Scenario

Turn one requests CIS376 and CIS410 with
mandatory Friday avoidance.

Turn two requests a preference for classes
starting after 10 AM while retaining the
previous courses and restrictions.

## CONFIRMED — Observed outcomes

| Trial | First-turn model calls | Second-turn model calls | Second-turn plans | Result |
|---|---:|---:|---:|---|
| 1 | 5 | 2 | 1 | Pass |
| 2 | 3 | 2 | 1 | Pass |
| 3 | 3 | 2 | 1 | Pass |

All three trials passed every recorded check.

Observed success rate: **3/3 (100%)**.

Across the three runs:

- Both CIS376 and CIS410 were preserved.
- Friday avoidance remained mandatory.
- Earliest start of 10:01 remained soft.
- Each second turn used one planning operation.
- Grounded, verified plan cards were returned.
- Updated authenticated plan context was confirmed.
- Browser chat returned HTTP 200 on both turns.
- Session revocation succeeded.
- No enrollment action was performed.

## CONFIRMED — Relationship to earlier work

The Step 123B pre-correction trial produced
two non-equivalent planning operations, including
one that omitted CIS410.

Step 127 completed successfully after the
deterministic preference-strength correction.

Step 129 repeated the corrected scenario
three times without an observed failure.

The existing multiple-plan validation restriction
remained enabled and unchanged.

## WORKING ASSUMPTION

Narrow, verified session-context reconstruction
combined with the deterministic planner can
support repeatable conversational scheduling
for supported synthetic request patterns.

## OPEN QUESTIONS

- Reliability over larger trial counts
- Performance on different follow-up phrasings
- Model behavior when planning results conflict
- Course additions and removals
- Concurrent session-update behavior
- Production Entra/Banner deployment approval
- User evaluation with realistic student wording

## RECOMMENDATION

Expand the evaluation matrix before making
general reliability or production-readiness claims.

Preserve all authorization, constraint-validation,
verified-card and no-enrollment safeguards.

## Research limitations

This is three executions of one synthetic
scenario, not an independent production study.

Model behavior can differ between executions,
even with temperature set to zero.

The observed 100% is a descriptive result,
not a reliable estimate of future success.

No real UNA student records, production Entra
integration, or enrollment transactions were used.

## Evidence

docs/evidence/2026-11-04-step129-three-trial-repeatability.json

The Master SOT v1.2 remains a draft.
