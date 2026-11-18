# Manual Leo Synthetic Demonstration

Date: 2026-11-03
Workstream: Leo UI / Authenticated Gateway / MCP
Starting commit: cf55376

## CONFIRMED — Implementation

A separate manual launcher was created:

scripts/leo_manual_demo.py

It uses the existing gateway, protected MCP academic
handlers, deterministic planner, synthetic Mock Banner
and original purple-and-gold Leo interface.

The demonstration binds to local loopback HTTPS
and generates an ephemeral self-signed certificate.

A research-only login link issues a server-side
student session using a locally signed synthetic JWT.

This is not a Microsoft Entra OAuth login.

The default production-oriented gateway does not
gain an anonymous or development login endpoint.

The launcher was changed to resolve its own Python
import path, removing the need for PYTHONPATH.

## CONFIRMED — Operator Observation

A real Microsoft Edge browser displayed the
result of the following prompt:

Plan CIS376 and CIS410

The user reported an answer and verified schedule
cards for SEC1001 and SEC2002 in 2027SP.

CIS376 was already registered in the synthetic
snapshot. CIS410 was proposed but not registered.

Total schedule credits: 6.

The UI explicitly stated that no enrollment occurred.

See:
docs/evidence/2026-11-03-step92-manual-demo-observation.md

## CONFIRMED — Limitations

The current manual demo supports one intentionally
scripted scheduling request.

It is not evidence of general conversational
AI capability or live LLM tool selection.

The local login is a synthetic demonstration bypass,
not a real institutional authentication solution.

The MCP service runs in the demonstration process.
Synthetic academic data is used exclusively.

The observation was user-reported rather than
captured by a new independent automated test.

## WORKING ASSUMPTION

The manual demo is suitable for demonstrating
the verified synthetic scheduling path locally,
provided its limitations are clearly disclosed.

## OPEN QUESTIONS

- Live AI integration and grounded fallback behavior
- RAG/OCR and additional question types
- Institution-approved Entra authentication
- Independently deployed MCP connectivity
- Persistent production-grade session management
- Final master SOT reconciliation

## RECOMMENDATION

Preserve this manual launcher separately from
production assembly and retain its explicit
synthetic-only restrictions.

Before expanding the demo, design and test the
live model's tool selection and fail-closed
handling of unverified scheduling claims.

The master SOT v1.2 remains a consolidation draft.
