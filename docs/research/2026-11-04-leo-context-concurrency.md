# Step 134 — Reject stale scheduling results

Date: 2026-11-04 (America/Los_Angeles)
Starting checkpoint: 61822957142927f6e4117bb362b32c0804a8aa4b
Branch: integration/browser-gateway-20261102

## Objective and scope

Address the concurrent-update question recorded in Step 133B before expanding
conversational edits. This phase adds optimistic concurrency control for the
existing single-process session store. It does not implement durable intent
storage, new scheduling grammar, enrollment, or production authentication.

## CONFIRMED findings

The new baseline regression file initially reported **8 failed, 2 passed**.
Two failures were missing snapshot/revision APIs. The behavioral failures showed
that overlapping requests could return stale results after another update or
context clear, and that cardless replies could return after logout or expiry.
The existing card-bearing logout/expiry cases already passed.

Each stored session now has a monotonically increasing, server-only plan revision.
The gateway reads the revision and plan context together. After the assistant
finishes and continuity validation completes, it atomically checks that the
session is still active and the revision is unchanged before saving a candidate
or releasing a reply.

- A successful verified context save increments the revision, including a save
  with unchanged values.
- Trusted writes and clears also increment the revision, preventing a
  clear-and-restore sequence from making a stale snapshot appear current.
- CSRF rotation preserves the revision.
- A cardless reply checks expiry and revision but does not change context.
- A stale result returns HTTP 409 without its model prose or plan cards.
- A revoked or expired session returns HTTP 401 at finalization.
- Only one of two simultaneous thread commits from the same revision succeeds.
- No lock is held across Ollama/MCP work, and one session's update does not
  invalidate another session's revision.

The browser handles 409 with fixed local text, preserves the editable message,
removes the loading indicator, and allows a deliberate retry. It does not display
arbitrary error-body text or automatically retry model requests.

Existing identity binding, token verification, CSRF/origin checks, continuity
comparison, multiple-plan guard, and no-enrollment boundary remain enabled.

### Validation

| Check | Actual result |
|---|---|
| Initial race regressions before implementation | 8 failed, 2 passed |
| Final concurrency regressions | 18 passed |
| Complete MCP/gateway suite | 299 passed |
| Complete AI-agent suite | 1,073 passed, 1 skipped |
| Chromium UI smoke | Passed: conflict, message preservation, retry, logout, wrong-student rejection, mobile layout |
| Live Chromium/Ollama three-turn continuity | Exit 0 |
| Python compilation and git diff --check | Passed |
| Existing live-evidence overwrite attempt | Rejected with exit 2; prior JSON hash unchanged |

The focused 18 cases are included in the 299-test suite. Concurrent route tests
use asyncio events, not timing sleeps; a separate two-thread barrier test checks
atomic commits. The browser conflict test uses intercepted synthetic responses;
it is not a real concurrent live-Ollama experiment. Node was unavailable in the
WSL command path for a standalone syntax check; Chromium parsed and executed the
actual changed JavaScript successfully.

The live trial used qwen3:4b-instruct at temperature 0.0 with synthetic OAuth and
Mock Banner, loopback HTTPS, and protected MCP through in-process ASGI transport.
It observed 3/2/2 model calls across three turns and one planner call per turn.
The Wednesday follow-up retained mandatory WED/FRI, soft earliest_start 10:01,
and requested CIS376/CIS410 in session context. As in Step 133B, the proposal
contained only online CIS410/SEC2002 with no meetings, with CIS376 excluded
because no open section fit the restrictions. Logout revoked the session.

The live probe now writes its screenshot alongside the supplied JSON filename
and rejects an existing JSON or matching PNG path. Step 133 evidence was not
overwritten. The console retains its historical Step 95 completion marker; the Step 134
evidence filenames, process exit status, and saved screenshot identify this run.

## WORKING ASSUMPTIONS

First successful verified completion wins for requests sharing a snapshot.
Rejecting a later stale result and asking the user to review/retry is preferable
to silently merging independently planned restrictions. This policy has been
implemented and tested locally; it has not been evaluated with real students.

## OPEN QUESTIONS

- Durable intent after an infeasible request is still not implemented; no
  verified candidate means the last verified context remains.
- A durable multi-worker store needs shared atomic revisions and centralized
  revocation. The current Python lock protects only one process.
- This guard is about server-side finalization, not network response ordering or
  synchronization of already displayed history across browser tabs.
- In-flight model work is not cancelled after another request commits or a
  session is revoked; its output is rejected on completion.
- Broader phrasing, mixed day strengths, and course additions/removals remain
  unsupported.
- Deterministic labels for partial-plan exclusions and realistic concurrency
  usability remain unvalidated.
- Production Entra/Banner access and a larger live evaluation remain outstanding.

## RECOMMENDATIONS

Retain optimistic revision checks when introducing future intent persistence.
Use a shared transactional store before multi-worker deployment. Prioritize
deterministic partial-plan exclusion labels next, then design how unsatisfied
intent should persist without weakening verified-proposal provenance.
Evaluate multi-tab retry behavior and larger independent live samples.

## Reproduction

From the repository root:

```bash
.venv/bin/python -m pytest -q tests/test_gateway_context_concurrency.py
.venv/bin/python -m pytest -q tests/
(cd ai-agent && ../.venv/bin/python -m pytest -q)
.venv/bin/python scripts/leo_live_ollama_browser_probe.py \
  --continuity-evidence docs/evidence/<new-trial-name>.json
```

The UI smoke runs scripts/leo_browser_smoke.py. For this checkpoint its EVIDENCE
directory was redirected to /tmp/una-step134-browser so existing Step 80
screenshots were preserved; only the new conflict screenshot was copied here.

## Evidence

- [Baseline failure summary](../evidence/2026-11-04-step134-before-test-summary.txt)
- [Concurrency regressions](../evidence/2026-11-04-step134-concurrency-tests.txt)
- [MCP/gateway suite](../evidence/2026-11-04-step134-mcp-tests.txt)
- [AI-agent suite](../evidence/2026-11-04-step134-agent-tests.txt)
- [Conflict UI screenshot](../evidence/2026-11-04-step134-conflict.png)
- [Live trial](../evidence/2026-11-04-step134-live-continuity-trial1.json)
- [Live screenshot](../evidence/2026-11-04-step134-live-continuity-trial1.png)
- [Validation provenance](../evidence/2026-11-04-step134-validation-metadata.json)

No credentials, authentication transcripts, or real academic records are included.
No enrollment operations were introduced. Master SOT v1.2 remains a draft, and
PR #3 remains draft.
