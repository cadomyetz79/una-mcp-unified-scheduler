# Chromium CI Runner Compatibility Correction

Date: 2026-11-03
Workstream: CI / Browser validation
Branch: integration/browser-gateway-20261102
Starting commit: 3fb58bf

## CONFIRMED — Observed Failure

The local Step 89 HTTPS browser-to-MCP test passed.

Both GitHub MCP integration checks on commit
3fb58bf succeeded.

The Chromium browser CI pull-request run failed
during Playwright browser dependency installation.

Failed GitHub run:
41751409108

Failed job:
126317105435

The log reported that the runner was using
Ubuntu 26.04, which Playwright 1.58.0 could not
support for Chromium dependency installation.

The Chromium test itself did not execute.

## CONFIRMED — Implementation Change

Updated:
.github/workflows/leo-browser-smoke.yml

Changed the GitHub Actions runner from:
ubuntu-latest

To:
ubuntu-24.04

The Playwright Python version remains pinned
to 1.58.0.

No scheduling, authentication, MCP, or Leo
application implementation was changed.

## OPEN QUESTION

The corrected workflow must run successfully
on GitHub before its status is classified
as passing.

## RECOMMENDATION

Keep the pull request in draft until the new
browser CI and MCP checks pass.

Maintain reproducible CI runner versions and
update them deliberately after compatibility
testing.

Master SOT v1.2 remains a consolidation draft.
