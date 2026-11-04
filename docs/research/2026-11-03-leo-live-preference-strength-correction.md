# Leo — Live Preference-Strength Failure and Correction

Date: 2026-11-03
Starting commit: 6c1e198

## Research objective

Investigate why the live Ollama two-turn scenario
treated a soft start-time preference as mandatory,
then correct the behavior without weakening the
existing student-data or schedule-verification rules.

## CONFIRMED — Live model observations

Model: qwen3:4b-instruct

In the first turn, the model produced one
successful planner call and verified schedule cards.

In the second turn, the model made two
successful planner calls:

1. CIS376 and CIS410
2. CIS376 only

The calls did not represent equivalent scheduling
requests and the agent withheld verified cards.

Both second-turn plans applied earliest_start=10:01
and incorrectly marked earliest_start as mandatory.

The live diagnostic returned HTTP 200 for both
turns after removing the diagnostic wrapper's
incorrect requirement that cards must exist.

## CONFIRMED — Root cause

The saved Ollama arguments included:

- earliest_start: None
- required_preferences: ["earliest_start"]

The deterministic parser correctly interpreted
the reconstructed student wording as soft.

The earlier preference reconciliation checked
only preferences for which the model supplied
a nonempty value. Thus, the incorrect mandatory
flag was retained when the time value was omitted.

The final constraint resolver recovered the
10:01 time but previously retained the
unsupported mandatory flag.

## CONFIRMED — Implementation correction

Changed:

- ai-agent/agent/constraints.py
- ai-agent/agent/assistant.py

Added:

- ai-agent/tests/test_live_followup_preference_strength.py

When a reliably parsed preference is explicitly
soft, the final resolver now clears an incorrect
mandatory flag.

The correction respects the existing
check_preference_language flag.

Normal operation enables the correction.
The research ablation disables this specific
correction, preserving baseline comparisons.

Mandatory Friday avoidance remains required.

## CONFIRMED — Verification

The full AI-agent and MCP/gateway test suites passed.

The two previously failing research-ablation tests
passed after the correction was made conditional.

The existing scripted two-turn Chromium HTTPS
integration passed again.

See:

docs/evidence/2026-11-03-step126-preference-regression.md

## WORKING ASSUMPTION

The deterministic classification of supported
English preference phrases provides an appropriate
safety check against model misclassification.

This has not been validated against unrestricted
real student language.

## OPEN QUESTIONS

- Whether live Ollama now preserves soft preferences
  during a fresh two-turn test
- Why the model requested CIS376 alone in its
  second planning call
- Whether repeated planning is avoidable
- How to handle conflicting multiple plans safely
- Concurrent session updates
- Broader follow-up language coverage

## RECOMMENDATION

Rerun the same live two-turn scenario after this
fix and record raw model planning arguments only
as bounded, sanitized synthetic metadata.

Do not relax the multiple-plan display guard or
the session-context validation policy without
an independently tested consistency rule.

## Research limitations

This is a correction supported by regression tests.
It is not yet a passing live Ollama two-turn trial.

No real Entra sign-in, live Banner student records,
or enrollment action was used.

The consolidated Master SOT v1.2 remains a draft.
This decision register entry is a phase record and
does not replace final master reconciliation.
