# Step 126 — Preference-Strength Correction Evidence

Date: 2026-11-03
Starting checkpoint: 6c1e198

## CONFIRMED — Test results

- New regression tests: 9 passed in 0.03s
- Research ablation tests: 2 passed in 0.99s
- Complete AI-agent suite: 1073 passed, 1 skipped in 10.79s
- Complete MCP/gateway suite: 255 passed in 2.42s
- Scripted HTTPS two-turn browser regression: passed
- Logout/session revocation regression: passed

## CONFIRMED — Regression behavior

The normal preference-language checker now corrects an incorrect model-supplied mandatory flag when the student's reliably parsed wording is soft.

The ablation setting continues to disable this specific preference-strength correction.

## Scope

These tests use synthetic data. The live Ollama two-turn scenario has not yet been rerun after this change.

The multi-plan display and context-validation restrictions remain unchanged.
