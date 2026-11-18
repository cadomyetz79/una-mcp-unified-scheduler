# Step 105 — Leo Safe Formatting Observation

Date: 2026-11-03
Checkpoint before commit: 8e63ee8
Interface: Live Ollama Leo demonstration
Student: S10001 (synthetic)
Term: 2027SP

## CONFIRMED — Operator-provided output

The operator tested:

"Plan CIS376 and CIS410, but I can't
have classes on Fridays."

The response showed readable course
information with bold labels and bullets.

The response identified:
- CIS376, SEC1001, Monday/Wednesday
- CIS410, SEC2002, online
- Six total proposed credits
- No Friday meetings in the proposal
- Compatibility with the existing
  synthetic CIS376 registration

The verified proposal cards remained
present in the copied output.

The interface stated that no enrollment
was performed.

## CONFIRMED — Automated checks

The Chromium test verified:

- Basic strong-text formatting
- Bullet-list formatting
- Literal display of injected HTML
- No creation of model-supplied HTML tags
- No execution of the tested HTML payload
- Authenticated MCP schedule cards
- Enter and Shift+Enter behavior
- Browser session revocation

The complete MCP and AI-agent suites
were also rerun in Step 106.

## Limitation

The preserved screenshot comes from the
scripted Chromium browser test, not from
the operator's live Ollama session.

The operator supplied the live-response
text as separate manual evidence.

Model replies are still untrusted input.
The renderer implements only a restricted
subset of Markdown.

Visual card spacing remains a potential
future user-interface improvement.
