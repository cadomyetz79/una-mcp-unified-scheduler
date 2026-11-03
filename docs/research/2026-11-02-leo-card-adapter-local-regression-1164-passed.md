# 2026-11-02 — Leo verified course-card adapter: local WSL regression evidence

**Workstream:** Unified MCP + Leo student-facing presentation integration, Step 40.  
**Classification:** **CONFIRMED** from WSL terminal output provided by the developer, with **OPEN QUESTIONS** below.  
**Git:** private `cadomyetz79/una-mcp-unified-scheduler`, `integration/leo-plan-cards-20261102`, branch head before this evidence file: `c9944f49c99135d00a578182945f244a6b2d1844`. Team source originally `a55813c` and imported personal RAGFlow/OCR commit `b54d20b`.

## Commands observed

The user verified the new checkout was on `main` at `b54d20b`, working tree clean, and `team-upstream` push URL `DISABLED`, then fetched and tracked `origin/integration/leo-plan-cards-20261102`.

```bash
.venv/bin/python -m pytest -q tests/test_unified_plan_cards.py
.venv/bin/python -m pytest -q tests/
(cd ai-agent && ../.venv/bin/python -m pytest -q)
git log -1 --oneline
git status --short
```

## Observed results — CONFIRMED

| Test scope | Result | Elapsed |
|---|---|---|
| Leo verified plan card adapter only | **23 passed** | **0.02 s** |
| Entire root Mock Banner / protected MCP / security / RAG+OCR contracts / Leo adapter | **128 passed**, 0 failed | **1.83 s** |
| Entire team AI agent and scheduling suite | **1,036 passed, 1 skipped**, 0 failed | **10.14 s** |
| Two complete suites, no double count | **1,164 passed, 1 skipped**, 0 failed | separate suites |

The focused 23 tests are included in the 128 root suite. The working tree was clean and `git log` showed `c9944f4` at the end. Marker: `UNIFIED_LEO_PLAN_ADAPTER_VERIFIED`.

## Design and limits

- **CONFIRMED source code:** `src/unified/plan_cards.py` takes a verified WS3 plan dict and a caller-supplied trusted synthetic student/term binding; it emits non-transactional `proposed_only` option cards, validates section IDs, meeting shapes, totals and registration-fit states, and refuses plan/student mismatches.
- **CONFIRMED:** The new adapter does **not** fetch missing course titles or individual credit hours and does **not** implement registration, RAG/AI orchestration or an actual browser.
- **OPEN QUESTION:** An authenticated server-side endpoint must bind expected student/term values to the session; the browser must not supply authorization identities. The planner-to-browser transport and authorized course enrichment require subsequent integration.
- **OPEN QUESTION:** The branch was locally tested, not yet verified on GitHub Actions at the time of this entry.
- **RECOMMENDATION:** Open a reviewable PR from this branch to the private unified repo's `main`, confirm CI status, merge only after appropriate review/checks. Append evidence of that outcome without rewriting these observations.

**Master SOT relationship:** This is additive evidence for the full-source SOT v1.2 reconciliation. It does not change the preserved personal v1.7 or historical team master v1.0.
