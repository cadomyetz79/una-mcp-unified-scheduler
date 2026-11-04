# Live Ollama to Protected MCP Browser Integration

Date: 2026-11-03
Workstream: AI Agent / MCP / Gateway / Leo
Starting commit: 9907669

## Objective

Test a real local AI model selecting scheduling
tools through the existing authenticated MCP
workflow and presenting verified proposal cards
in a real browser.

## CONFIRMED — Implementation

Added the isolated test:

scripts/leo_live_ollama_browser_probe.py

It reuses the previously verified synthetic
OAuth, HTTPS gateway, protected MCP handlers,
deterministic planner and Leo browser UI.

Instead of ScriptedLLM, this test uses:

OllamaLLM(model="qwen3:4b-instruct")

The test checks that the model successfully
selects and executes plan_schedule, that the
agent produces a grounded result, and that
verified student-specific cards are returned.

The existing scripted tests remain unchanged.

## CONFIRMED — Observed Results

The test reported:

- Two live-model calls
- One successful model-selected plan_schedule call
- Agent stopped_reason: answered
- Grounded plan-card assertions passed
- Browser chat returned HTTP 200
- Leo rendered verified schedule cards
- Logout revoked the browser session
- Subsequent session access returned HTTP 401

The complete live browser probe passed.

## CONFIRMED — Security Boundaries

Student identity is supplied by a verified
synthetic server-side session.

MCP independently verifies delegated access.

The model does not determine academic validity.
Deterministic scheduling code performs validation.

The browser displays cards projected from
verified scheduling results.

No registration or enrollment was performed.

## LIMITATIONS

This was a single live-model scheduling scenario.

It does not demonstrate general reliability across
different questions, constraints, or model failures.

Authentication is simulated, not real Entra.

The protected MCP server uses an in-process
ASGI transport for this test.

The backend uses synthetic academic records.

The local Ollama model does not require an
external AI API.

## WORKING ASSUMPTION

The existing Ollama adapter can support a
controlled live conversational Leo demonstration.

## OPEN QUESTIONS

- Accuracy across varied scheduling requests
- Grounded fallback during live-model failures
- Live-model latency and resource consumption
- Multi-turn conversation persistence
- RAG and OCR integration
- Institution-approved Entra authentication
- Separately deployed MCP transport
- Final master SOT reconciliation

## RECOMMENDATION

Preserve this isolated probe as the baseline
for future live-model integration.

Next, introduce an explicitly local-only
manual Leo mode using the real Ollama model.

Keep scripted and live-model demonstrations
separate to preserve reproducibility.

Do not merge demo-only synthetic authentication
into production application assembly.

Master SOT v1.2 remains a consolidation draft.
