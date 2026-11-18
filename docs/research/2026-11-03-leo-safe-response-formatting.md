# Leo Safe Response Formatting

Date: 2026-11-03
Starting commit: 8e63ee8

## Objective

Improve the readability of Leo's AI-generated
answers without permitting untrusted content
to become executable browser HTML.

## CONFIRMED — Implementation

Modified:
- src/gateway/leo_ui/unified.js
- src/gateway/leo_ui/interactive.css
- scripts/leo_local_https_demo.py

The formatter supports a deliberately
limited subset of display formatting:

- Bold text
- Unordered bullet lists
- Paragraph separation
- Normalization of selected escaped
  characters observed in Ollama output

The formatter uses fixed DOM elements
and text nodes.

User-authored and model-authored HTML
is not interpreted as executable markup.

The formatter has output-size limits.

## CONFIRMED — Security validation

The Chromium test includes an HTML
injection attempt as untrusted text.

The test asserts that no corresponding
HTML image element is created and the
tested JavaScript payload does not run.

The test also verifies the existing
authenticated scheduling and logout flow.

## CONFIRMED — Functional validation

The operator provided a live Ollama
scheduling response showing improved
formatting and preserved proposal cards.

The demonstrated schedule respected the
no-Friday restriction for synthetic
student S10001 in term 2027SP.

No enrollment operation was performed.

## CONFIRMED — Regression evidence

The Step 104 local run reported:
- 206 MCP tests passed
- 1051 AI-agent tests passed
- 1 AI-agent test skipped

Step 106 reruns these suites and the
Chromium integration test before commit.

## WORKING ASSUMPTION

The restricted formatter is adequate
for current research demonstrations.

## OPEN QUESTIONS

- Improve schedule-card spacing
- Improve nested-list presentation
- Support additional Markdown constructs
- Strengthen model-answer wording
- Generalize academic evidence enforcement
- Implement multi-turn context
- Integrate approved production services

## RECOMMENDATION

Keep model-generated HTML inert.

Preserve the authenticated gateway,
MCP authorization and deterministic
academic validation boundaries.

Continue recording live-model observations
separately from scripted browser tests.
