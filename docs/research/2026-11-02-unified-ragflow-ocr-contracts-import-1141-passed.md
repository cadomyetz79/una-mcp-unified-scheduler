# 2026-11-02 — Unified repository: personal RAGFlow and OCR evidence contracts imported and tested

**Phase:** unified source consolidation, Gate C. **Workstreams:** integrated WS1–WS4 team baseline plus separate personal research adapters. **Evidence:** user-provided WSL terminal output on 2026-11-02; user output includes commands, test results, `git status`, and completion marker `UNIFIED_RAG_OCR_CONTRACTS_VERIFIED`.

## CONFIRMED baseline and exact procedure
- The isolated team-based checkout is `~/una-mcp-unified-scheduler`, branch `integration/unified-baseline-20261102`, based on merged team `main` `a55813c464ac3b4587a935b63aae444219651222`.
- In the new checkout, the existing remote `team-upstream` push URL was set to `DISABLED`, which stops an accidental push to the original team repo.
- The personal research checkout `~/una-mcp-sot-v17-work` was fast-forwarded to commit `8c845026d597b1faaa4a98452e1cbf57577f0f33`; it contains the canonical personal SOT v1.7 and Master full-source draft v1.2.
- The following **six unmodified personal source files** were copied into the new integration checkout using `cp` and verified with `cmp -s`: `src/agent/__init__.py`, `src/agent/knowledge_retrieval.py`, `src/agent/ragflow_adapter.py`, `src/agent/ocr_transcript_handoff.py`, `tests/test_ragflow_adapter.py`, and `tests/test_ocr_transcript_handoff.py`.
- No pre-existing destination file was overwritten, and the team planning and MCP code was not changed by this import.

## CONFIRMED observed tests
- `.venv/bin/python -m pytest -q tests/test_ragflow_adapter.py tests/test_ocr_transcript_handoff.py`: **38 passed in 0.06 s**.
- `.venv/bin/python -m pytest -q tests/`: **105 passed in 1.85 s**. This root count **includes** the preceding 38 focused tests.
- In `ai-agent/`: `../.venv/bin/python -m pytest -q`: **1036 passed, 1 skipped in 9.93 s**.
- Combined full-suite unique executed count: **1141 passed and 1 skipped**, **0 failed**. This measures offline tests in the integrated checkout; it does not demonstrate a complete, live single-agent RAG/OCR system.
- `git status --short` showed new untracked `src/agent/`, `tests/test_ragflow_adapter.py`, and `tests/test_ocr_transcript_handoff.py`; no commit or push was reported at the conclusion of Step 37.

## Architectural decisions / caveats
- **RECOMMENDATION:** Keep the team six-tool authenticated MCP and WS3 deterministic planning/runtime as authoritative. The imported read-only policy retriever and RAGFlow adapter are an optional *public/synthetic knowledge* boundary; they must not receive student transcripts or session credentials. Do not claim a live team RAGFlow dataset has been connected.
- **RECOMMENDATION:** Keep OCR evidence synthetic, student-bound, provenance-checked and non-authoritative. The imported validator is **not** an OCR engine; it cannot itself verify a grade or satisfy a prerequisite.
- **OPEN QUESTION:** Safely connect the retrieval and OCR components through the one unified agent and the final Leo browser gateway. Preserve error isolation and fail-closed authorization.
- **OPEN QUESTION:** Live institutional Entra, production Banner, approved school data and registration remain outside this phase.
- **RECOMMENDATION:** Commit only the six imported files plus a dated evidence record to the local integration branch, recording source checksums; then create a **new private** remote for the unified implementation and verify end-to-end agent/browser behavior separately.

**Source of Truth:** additive evidence entry for reconciliation into the Master full-source v1.2 draft. Its historical paragraphs/tables are preserved; visual and factual reconciliation remain pending.
