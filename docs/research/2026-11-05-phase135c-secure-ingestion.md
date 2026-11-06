# Phase 135C — Synthetic ACL ingestion
Date: 2026-11-05 (America/Los_Angeles). Workstream: security/RAG integration.
Base implementation: 7e4f092db3ef7c595c55f1e0d30b5e409bba6942.

## CONFIRMED
src/agent/secure_ingestion.py validates explicit synthetic source URI, dataset/domain,
classification and DocumentACL before invoking the parser. Each segment is a
separate document ID; complete ACL/provenance and a content digest accompany every
derived chunk. No OCR, real document, or remote vector writes are claimed.
Atomic staging prevents partial writes after parser failure. Revisions detect
policy changes during parsing. Versioned updates invalidate old chunks; revocation
removes chunks and prevents re-ingestion under the revoked record.

Tests: .venv/bin/python -m pytest -q tests/test_secure_ingestion.py: 13 passed.
Full root suite: 383 passed. Evidence: docs/evidence/2026-11-05-135c-*.txt.
Phase 135B exact-SHA GitHub workflows were all completed successfully when checked.
Original handout remains unavailable locally; committed summary guides this phase.

## WORKING ASSUMPTION
Separate source segments with independent ACLs are the minimal safe representation
for mixed permissions. The registry is an authoritative in-memory synthetic
contract, not a durable production database or actual RAGFlow ingestion.

## OPEN QUESTION
Remote metadata propagation, transactional vector publication, durable recovery,
real source ownership and approved corpus access require live backend validation.
Windows Docker daemon is unavailable and no WSL RAGFlow port is listening.

## RECOMMENDATION
Do not activate HTTP protected retrieval from source inspection alone. Require
deployment-specific prefilter evidence, use an explicit nonempty authorized
document list, and independently check returned metadata and content provenance.
