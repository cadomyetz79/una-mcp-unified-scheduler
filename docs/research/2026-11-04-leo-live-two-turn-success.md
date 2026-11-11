# Leo — Live Two-Turn Ollama Scheduling Validation

Evaluation date: 2026-11-04

## Research objective

Evaluate whether the Step 126 deterministic
preference-strength correction works in a live
two-turn Ollama conversation using authenticated
synthetic scheduling services.

## CONFIRMED — Test environment

- Model: qwen3:4b-instruct
- Starting checkpoint: bbeeda3
- Real Chromium browser with loopback HTTPS
- Synthetic OAuth identity approval
- Protected MCP academic tools
- Synthetic Mock Banner data
- Deterministic WS3 scheduling planner
- No enrollment actions

## CONFIRMED — Student interaction

First turn:
Plan CIS376 and CIS410, but I cannot have
classes on Fridays.

Second turn:
Actually, I'd prefer classes that start
after 10 AM. Keep everything else the same.

The application reconstructed the second request
using previously verified session context.

## CONFIRMED — Before correction

Checkpoint: 6c1e198

- Second-turn model calls: 4
- Second-turn planner calls: 2
- First plan requested CIS376 and CIS410
- Second plan requested only CIS376
- The 10:01 start preference was marked mandatory
- Verified cards were withheld

## CONFIRMED — After correction

Checkpoint: bbeeda3

- First-turn model calls: 5
- Second-turn model calls: 2
- Second-turn planner calls: 1
- Both CIS376 and CIS410 were preserved
- Friday avoidance remained mandatory
- 10:01 earliest start remained soft
- Proposed section IDs: SEC1001 and SEC2002
- Verified schedule cards were returned
- The browser chat returned HTTP 200
- Verified session plan context was updated
- The live two-turn evaluation completed

The model still supplied a mandatory earliest-start
flag without supplying an earliest-start value.

The corrected deterministic resolver recovered the
10:01 value and removed that unsupported mandatory
flag based on the student's explicit soft wording.

## CONFIRMED — Safety

The multiple-planning-call display restriction
was not removed or weakened.

The session-context projector continues to require
one successful, verified planning operation.

The returned schedules remain proposals only.
No enrollment was performed.

## CONFIRMED — Prior test evidence

The Step 126 checkpoint passed:

- 1,073 AI-agent tests, 1 skipped
- 255 MCP/gateway tests
- Scripted two-turn Chromium HTTPS validation
- Research-ablation regression tests

These tests were not rerun as part of this
documentation-only Step 128.

## WORKING ASSUMPTION

Narrow server-side follow-up reconstruction
combined with deterministic preference
validation can support a useful conversational
course-scheduling prototype.

## OPEN QUESTIONS

- Reliability across repeated live-model trials
- Whether different prompts trigger extra planning
- Handling conflicting multiple planning calls
- Broader follow-up language and course changes
- Concurrent session updates
- Production-grade identity and deployment

## RECOMMENDATION

Preserve the verified behavior and expand
live evaluation cases without weakening
the planning, identity, or evidence guards.

## Research limitations

This is one successful post-fix live-model trial.
The reduced number of planning calls may reflect
model variability; a causal improvement in model
tool selection has not been established.

The synthetic prototype has not been validated
with real student records or deployed at UNA.

Machine-readable bounded evidence:
docs/evidence/2026-11-04-step127-live-comparison.json

The Master SOT v1.2 remains a consolidation draft.
