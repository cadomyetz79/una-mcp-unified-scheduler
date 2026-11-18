# Phase 135B — MCP execution authorization
Date: 2026-11-05 (America/Los_Angeles). Workstream: security/integration.
Base: 3be5b732565c58a8f2974bd075da627c343d79c1.

## CONFIRMED
All six academic MCP handlers call server-owned role/scope authorization before
backend access. Trusted deployment tenant/audience/issuer are checked; mapped
student identity is required, and student-specific ownership remains independent.
Unknown tool policies deny. Synthetic legitimate fixtures explicitly carry
RAG.Student. No production UNA role assignments were invented.

The Phase 135A normalizer now rejects non-finite expiry, malformed group-overage
indicators, unbounded/control-character claim values, and contradictory
public/authenticated ACLs containing restrictive predicates. Group-dependent
authorization fails closed without Graph resolution. Safe logs contain only
allow/deny decisions, not tokens, identity fields, prompts, or records.

Tests: .venv/bin/python -m pytest -q tests/: 370 passed.
cd ai-agent && ../.venv/bin/python -m pytest -q: 1073 passed, 1 skipped.
Focused pre-regression run: 44 passed. New execution tests exercise all six
handlers against Student/Faculty/HR/Finance/Legal fixture roles, group revocation,
unknown tools and malformed claims. Signed HTTP MCP tests deny non-student roles
even when tools are advertised. Existing signature/expiry/audience/tenant tests
remain in the full root suite.

Changed paths: src/mcp_server/{entra_rbac_acl,team_security,team_protected_server}.py;
tests/test_entra_mcp_execution.py; protected MCP/browser integration fixtures;
synthetic scripts/leo_* and live_team_mcp_chat.py.
Evidence: docs/evidence/2026-11-05-135b-{root,agent}.txt.
No real Entra tenant or enrollment operations were used.

## WORKING ASSUMPTION
RAG.Student is the synthetic academic policy role; production configuration
requires institutional approval. Refreshed tokens are evaluated per request;
existing unexpired JWTs do not provide immediate directory-revocation detection.

## OPEN QUESTION
Microsoft Graph membership resolution and real university role provisioning remain
unavailable. The original professor handout was not found in searched local
Documents/attachments/home paths; the committed phase135 summary is the source used.

## RECOMMENDATION
Proceed with pre-parse ACL validation, atomic synthetic ingestion, and explicitly
gated retrieval capability validation; never substitute an unverified backend
filter or empty candidate set for authorization.

CONFIRMED evidence handling: temporary logs were unavailable at preservation time; both suites were rerun directly into repository evidence files with the same counts.
