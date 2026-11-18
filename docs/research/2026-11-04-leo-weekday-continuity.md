# Step 133B — Verified weekday continuity

Date: 2026-11-04 (America/Los_Angeles)
Starting checkpoint: 1406ee801096c230b82d086f0a1e66f7b3f9e284
Branch: integration/browser-gateway-20261102

## CONFIRMED findings

The gateway reconstructs the supported Wednesday addition from authenticated,
verified plan context. It preserves requested courses, term, existing mandatory
days, and the values and strengths of time preferences. It rejects mixing a
new mandatory day with previously soft avoided days because the current schema
cannot represent different strengths for individual days.

Before displaying continuation cards or replacing context, the gateway compares
the candidate planner inputs against the permitted change. Lost days, softened
mandatory restrictions, unrelated time/course/term changes, missing verified
context, and unsupported continuations fail closed. The multiple-plan guard,
identity binding, CSRF/origin checks, privacy guards, and no-enrollment boundary
remain in place.

Review corrections additionally bind an explicit new-schedule reset to its
requested courses and term, reject unrequested reset preferences, and compare
day sets without treating a harmless ordering change as a different restriction.
The refusal now gives an explicit supported reset example rather than implying
that an arbitrary complete restatement is supported.

### Live Chromium / Ollama result

The reproducible probe is:

```bash
.venv/bin/python scripts/leo_live_ollama_browser_probe.py \
  --continuity-evidence docs/evidence/<new-trial-name>.json
```

Use a new evidence filename for each execution. The continuity screenshot has a
fixed Step 133 filename and should be preserved separately before another run.

The live model was qwen3:4b-instruct at temperature 0.0, think=False,
num_ctx=8192, and num_predict=512. Real Chromium used loopback HTTPS, synthetic
OAuth approval with locally signed tokens, authenticated gateway requests,
protected MCP through in-process ASGI transport, and unmodified Mock Banner data.

The corrected trial completed all three turns:

| Turn | Request | Model calls | Successful planner calls | Outcome |
|---|---|---:|---:|---|
| 1 | CIS376 + CIS410; Friday mandatory | 3 | 1 | Grounded proposal and Friday context saved |
| 2 | Prefer starting after 10 AM; retain everything else | 2 | 1 | Friday mandatory; 10:01 soft; both requested courses retained |
| 3 | Cannot attend Wednesdays either; retain everything else | 2 | 1 | Wednesday + Friday mandatory; 10:01 soft; both requested courses retained |

The Wednesday response returned HTTP 200 and grounded verified cards. The actual
proposal contained only CIS410/SEC2002, an online section with no meetings.
CIS376 was explicitly excluded with NO_SECTION_MATCHES_PREFERENCES: its open
section meets Wednesday and its Tuesday/Thursday alternative is full. The browser
explanation visibly identified CIS376 and both excluded weekdays. The saved
context still requested CIS376 and CIS410, with avoid_days WED/FRI and required
avoid_days. A partial proposal is not evidence that both courses are schedulable.

Logout succeeded, the server session count reached zero, and a subsequent browser
session check returned 401. No enrollment or registration change occurred.
The Wednesday-free proposal does not establish that the student's unchanged
existing registration is Wednesday-free.

### Failures retained rather than rewritten

The first live execution preserved both mandatory weekdays in planner inputs
and saved context, but the probe exited 1 before logout because it incorrectly
asserted zero options. Inspection of planner.py established that partial proposals
are supported. The corrected probe verifies the partial option, its meeting days,
the exclusion reason, the displayed course explanation, and saved context.
Trial 1 remains recorded with passed=false; trial 2 records passed=true.
This is one fully passing probe out of two executions, not two passing trials
and not a reliability estimate.

The initial expanded unit-test run reported 24 passed / 1 failed because the new
test expected the verdict name "preferred"; the existing extractor uses "soft".
The expectation was corrected to the actual interface. Final results are below.

### Final regression results

| Command | Actual result |
|---|---|
| .venv/bin/python -m pytest -q tests/test_gateway_day_continuity.py | 26 passed |
| .venv/bin/python -m pytest -q tests/ | 281 passed |
| cd ai-agent && ../.venv/bin/python -m pytest -q | 1,073 passed, 1 skipped |
| Live Chromium probe, corrected trial 2 | Exit 0; three turns, partial proposal and logout verified |
| Python compilation and git diff --check | Passed |

The 26 focused cases are included in the 281-test suite, not additional tests.
They cover reconstruction, loss of either day, extra days, strength changes,
time/course/term changes, unsupported wording, soft-day rejection, reset binding,
day-order equivalence, and preserving requested courses after a partial proposal.

## WORKING ASSUMPTIONS

- Narrow deterministic reconstruction plus verified planner evidence is suitable
  for the supported synthetic follow-up grammar.
- Retaining requested courses across partial proposals is the intended continuity
  contract; proposed sections may be only a subset, with exclusions explained.
- The observed model behavior may vary across executions even at temperature zero.

## OPEN QUESTIONS

- Broader natural-language phrasing, course additions/removals, and mixed
  soft/mandatory day preferences remain unsupported.
- Concurrent requests can read the same prior context; this change does not add
  serialized session updates or compare-and-swap semantics.
- If no verified proposal can be saved, context remains the last verified proposal;
  durable intent tracking for infeasible requests is not implemented here.
- Partial-plan exclusion information currently relies on model explanation in the
  browser; the card contract itself does not contain an exclusion field.
- Production Entra/Banner approval, realistic student wording, and larger
  repeatability studies remain outstanding.

## RECOMMENDATIONS

Preserve the narrow grammar and fail-closed checks. Add an explicitly designed
intent/context versioning workflow before extending unsupported edits or
concurrent updates. Evaluate deterministic exclusion labels for partial cards.
Expand independent synthetic and realistic wording trials before making
production-readiness or general success-rate claims.

## Evidence

- [Trial 1, retained failed probe](../evidence/2026-11-04-step133-live-continuity-trial1.json)
- [Trial 2, corrected passing probe](../evidence/2026-11-04-step133-live-continuity-trial2.json)
- [Model and fixture provenance](../evidence/2026-11-04-step133-validation-metadata.json)
- [Browser screenshot](../evidence/2026-11-04-step133-continuity.png)
- [Focused continuity tests](../evidence/2026-11-04-step133-continuity-tests.txt)
- [MCP/gateway suite](../evidence/2026-11-04-step133-mcp-tests.txt)
- [AI-agent suite](../evidence/2026-11-04-step133-agent-tests.txt)

Evidence contains synthetic academic fields and bounded test summaries, not bearer
tokens, cookies, CSRF values, private keys, or raw authentication traces.
Master SOT v1.2 remains a consolidation draft. PR #3 remains draft.
