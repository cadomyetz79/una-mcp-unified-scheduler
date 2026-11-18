# Phase 135F — Leo live integration closeout (2026-11-05)

Starting feature checkpoint: `ab5056b`.
Workstream: unified Leo UI, scheduling continuity, authorization integration.
Research question remains unchanged.

## CONFIRMED

- The unfinished Phase 135F changes add deterministic partial-proposal
  and exclusion metadata to authenticated verified schedule cards.
- Leo displays the exclusion reason directly from verified planner data.
- The first live trial failed after a valid first-turn schedule because
  context revalidation attempted to reproject a model-visible trace
  from which `student_id` had intentionally been removed.
- The correction independently compares requested courses, exclusion
  codes, trusted reason mappings, and proposal completeness with the
  trace, while preserving the authenticated-student checks.
- A later protected-knowledge browser attempt failed because its
  test expected chunk-only IDs instead of dataset/document/chunk IDs.
  Another test assertion expected a generic blocked record rather
  than the actual `system_privacy` denial.
- These test expectations were corrected without weakening access
  controls or changing application retrieval permissions.
- Live five-turn Chromium + Ollama synthetic trial passed:
  three scheduling turns, an authorized policy query, and a denied
  foreign-student-record request.
- Wednesday and Friday mandatory restrictions and the 10:01 soft
  start preference were preserved.
- Final proposal contained CIS410 SEC2002; CIS376 was excluded
  with `NO_SECTION_MATCHES_PREFERENCES`.
- Logout revoked the authenticated browser session.
- The foreign-student request used zero model calls.
- Final root suite: 432 passed.
- Final AI-agent suite: 1,073 passed, 1 skipped.
- Focused security/context tests: 57 passed.
- These test counts overlap and must not be added together.

## CONFIRMED evidence and changes

Source files:
`scripts/leo_browser_smoke.py`,
`scripts/leo_live_ollama_browser_probe.py`,
`src/gateway/leo_ui/unified.js`,
`src/gateway/plan_context.py`,
`src/unified/plan_cards.py`,
`tests/test_unified_plan_cards.py`,
`tests/test_gateway_verified_plan_context.py`.

Sanitized live result:
`docs/evidence/2026-11-05-135f-final-live-summary.json`.

Test output:
`docs/evidence/2026-11-05-135f-final-root.txt`;
`docs/evidence/2026-11-05-135f-final-agent.txt`.

Original failed attempts and full new live trial files remain in
the local research-evaluations/evidence directories.
A Phase 135F recovery archive was created before source edits.
This checkpoint does not overwrite historical evidence.

## WORKING ASSUMPTION

The bounded synthetic browser workflow is suitable for demonstration,
but a single successful live five-turn run is not a reliability estimate.

## OPEN QUESTIONS

- Live protected RAGFlow pre-ranking filter behavior remains unverified.
- The actual UNA Entra tenant, Graph group refresh, production Banner,
  real institutional policies, and student enrollment are not connected.
- The research prototype still needs the live RAGFlow integration phase.

## RECOMMENDATION

Commit this checkpoint after staged-file review. Keep PR #3 draft.
Start RAGFlow with synthetic data only, and verify authorization filters
before enabling protected HTTP retrieval. Record exact CI results
after the new commit is pushed.
