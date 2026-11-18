# Step 103 — Leo Browser and Evidence Observations

Date: 2026-11-03
Environment: WSL and Microsoft Edge
Student: S10001 (synthetic)
Term: 2027SP

## CONFIRMED — Operator-reported observations

The operator tested the live Ollama Leo interface.

Academic history question:
Leo returned CIS225, CIS236 and CIS330 from
the authenticated synthetic academic record.

CIS410 prerequisite question:
Leo identified CIS330 as the prerequisite
and reported it satisfied in the synthetic
academic history.

Friday scheduling restriction:
Leo returned SEC1001 and SEC2002 as a
verified synthetic proposal.

The proposal respected the no-Friday restriction.
The UI stated that no enrollment occurred.

Keyboard interaction:
The operator confirmed that Enter-to-send worked.

The Chromium keyboard regression was added
to the existing automated browser test.

## CONFIRMED — Regression findings

The initial evidence-router implementation
interrupted an existing model-led workflow.

The revised implementation permits model tool
selection before applying deterministic
academic evidence enforcement.

The corrected local tests passed in Step 100A:
1051 agent tests passed, 1 skipped;
206 MCP tests passed.

Step 103 regression outputs are stored separately.

## Limitations

These manual observations are operator-reported.
The demo uses synthetic identity and Mock Banner.
No real Entra or Banner service was accessed.
No enrollment capability exists.

Academic evidence enforcement currently recognizes
a narrow set of question patterns.

Multi-turn conversational memory is not verified.
