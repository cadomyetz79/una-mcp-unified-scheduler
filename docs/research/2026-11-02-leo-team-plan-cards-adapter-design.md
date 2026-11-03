# 2026-11-02 — Leo verified team-plan card adapter (candidate)

**Status: IMPLEMENTED ON FEATURE BRANCH; UNIFIED WSL REGRESSION PENDING.**
**Branch:** `integration/leo-plan-cards-20261102` in the new **private** `cadomyetz79/una-mcp-unified-scheduler` repository.
**Source baseline:** team merged main `a55813c` + personal RAGFlow/OCR contract import `b54d20b`. Original team and personal repos unchanged.

## Scope and decisions

- **CONFIRMED from inspected team code:** WS3's `agent.planner.plan_schedules()` returns a `PlanResult.to_dict()` with the bound `student_id`, `term_id`, `current_registrations_checked`, `current_registrations`, and `options[]`. Each option includes `section_ids`, total `total_credit_hours`, `rank`, `registration_fit`, and `sections[]`. Sections provide IDs, course IDs, modality, seat snapshot and meeting details. Individual course titles and credit hours are not carried in these option-section dictionaries.
- **RECOMMENDATION (implemented as a first-stage pure adapter):** `src/unified/plan_cards.py` turns only a verified WS3 planner dictionary into a minimal Leo UI view-model. The expected student and term must come from a trusted server session; mismatched identity or term fails closed. Reject malformed section/meeting fields, contradictory registration status, duplicated IDs and unverified option ranks.
- **CONFIRMED design limitation:** Output status is always `proposed_only`; existing registration is labeled from the verified synthetic registration snapshot only. No registration operation is performed, and no invented course title or per-course credit is returned.
- **RECOMMENDATION:** The browser must use text-safe DOM APIs (e.g. `textContent`) and should not accept model-provided HTML. The adapter never constructs HTML.
- **OPEN QUESTION:** Enriching course cards with names/credits requires a separate authorized WS2 `get_course` lookup with a validated join. Do not fill missing details from LLM prose.
- **OPEN QUESTION:** The adapter is not yet wired to Leo's authenticated gateway, the WS3 AssistantResult tool trace, or team RAG/OCR. Live model+browser integration requires a later end-to-end test.
- **OPEN QUESTION:** This prototype uses a strict `S12345` synthetic student-ID format; real identity mapping depends on university approval and review.

## Evidence and tests

- **CONFIRMED, isolated author-side test only:** 23 standalone pytest tests passed against the new module in a temporary copy; this does not prove that the new private repository's complete test suites pass.
- **PENDING USER-OBSERVED EVIDENCE:** `.venv/bin/python -m pytest -q tests/test_unified_plan_cards.py`, then `.venv/bin/python -m pytest -q tests/`, then the existing complete `ai-agent/` tests.
- **Baseline historical result:** 1,141 passing offline tests, 1 skipped after RAGFlow/OCR import in `b54d20b`; repeat the suites before promoting this feature.
- **Deployment/security:** Only synthetic fixtures; not an official UNA Banner/Entra connection; no real transcript ingestion, no enrollment.

This file is an additive decision record for the master SOT reconciliation. Do not overwrite historical test counts, historical SOT documents, or production readiness labels.
