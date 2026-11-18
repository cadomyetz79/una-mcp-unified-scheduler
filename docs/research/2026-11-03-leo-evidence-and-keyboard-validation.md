# Leo Academic Evidence and Keyboard Improvements

Date: 2026-11-03
Starting checkpoint: 4c866c6
Workstreams: AI Agent, MCP, Gateway, Leo UI

## Objective

Correct two observed live-model evidence failures
and improve Leo's chat input experience.

## CONFIRMED — Evidence failures

The Step 98 probe reproduced zero model tool calls
for completed-course and prerequisite questions.

Step 99 showed that stronger prompt instructions
improved initial tool selection but did not
guarantee retrieval of suitable evidence.

## CONFIRMED — Implementation

New files:
- ai-agent/agent/academic_evidence.py
- ai-agent/tests/test_academic_evidence_router.py
- scripts/leo_live_manual_demo.py

Modified files:
- ai-agent/agent/assistant.py
- scripts/leo_local_https_demo.py
- src/gateway/leo_ui/unified.js

The evidence router addresses two narrowly defined
academic questions using authenticated MCP data.

An initial implementation answered before the model,
causing an existing E17 regression.

The corrected implementation preserves model-led
tool execution before enforcing factual evidence.

The Leo UI now uses Enter for submission and
Shift+Enter for multiline input through the
existing authenticated form handler.

## CONFIRMED — Validation

The operator reported correct academic-history,
prerequisite and scheduling responses in Edge.

The operator also confirmed Enter-key submission.

Automated regression results are retained in
Step 103 evidence files.

Node.js was unavailable in the current WSL shell,
so its optional JavaScript syntax check was skipped.
This is not recorded as a passing Node.js check.

## Security and reproducibility

The interface retains session and CSRF protection.

Academic records remain scoped to the authenticated
synthetic student.

Deterministic logic remains responsible for
academic eligibility and schedule validation.

The live demo is isolated from production
authentication and uses synthetic data.

No enrollment tools were added.

## WORKING ASSUMPTION

The current narrow evidence-routing approach can
be extended after additional regression testing.

## OPEN QUESTIONS

- Generalized academic evidence orchestration
- Multi-turn conversational context
- Safe rich-text response rendering
- Live-model accuracy across varied questions
- RAG and OCR integration
- Institution-approved Entra and Banner access
- Final master SOT consolidation

## RECOMMENDATION

Continue to separate LLM interpretation from
deterministic academic evidence and validation.

Preserve the scripted and live manual demonstrations.
Do not introduce research-only authentication into
the production application.
