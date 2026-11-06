# Phase 135A — Professor's Entra MCP + RAG authorization requirements and first tested contracts

**Date:** 2026-11-05 (America/Chicago). **Owner/workstream:** unified MCP security + RAG coordination.  
**Starting source:** GitHub feature branch `integration/browser-gateway-20261102`, checkpoint `068bc0a`.  
**Professor reference:** *Entra_ID_MCP_RAG_Authorization_Student_Handout.docx*, 15 pages, provided 2026-11-05. The handout is retained outside this repository; this record paraphrases its implementation requirements and cites page locations.  
**Status:** Foundation committed and CI-tested. **NOT** protected RAG deployment.

## Research question and scope

The original research question remains unchanged:

> How do we create an MCP server integrated with Entra and an AI agent to help schedule classes for students at UNA?

The handout refines **how** Entra-derived privileges must control MCP and knowledge retrieval, not the research question. No approval for live Entra, production Banner, private student documents, or registration writes is implied.

## Handout requirements — classified

- **PROFESSOR REQUIREMENT (pages 2–4):** validate Entra JWT first, derive `tid`, `oid`, `roles[]`, `groups[]`, and `scp` into a trusted server-side request context; enforce role/group and scope authorization at tool execution; never accept role/group/tenant/identity arguments from the model.
- **PROFESSOR REQUIREMENT (pages 5–6):** resolve document permissions **before** parsing/chunking; reject missing or conflicting ACL metadata; inherit the validated ACL into every chunk/vector record; coordinate persistence and verify ACL parity.
- **PROFESSOR REQUIREMENT (pages 6–11):** pre-filter retrieval by tenant, domain, visibility, and role/group/user ACL; use the actual installed vector backend's supported filters; verify every returned chunk/row again before LLM context assembly; reject policy version/hash mismatch.
- **PROFESSOR REQUIREMENT (pages 11–13):** handle role/group revocation and group-claim overage, use minimal audit logs, and run the five-identity Student/Faculty/HR/Finance/Legal matrix plus negative tests, including stale ACL and prompt injection.
- **DESIGN NOTE (pages 1, 6, 15):** PostgreSQL + pgvector is a reference implementation. An existing RAGFlow Elasticsearch/OpenSearch/Infinity backend may use equivalent authorization controls; do not assume pgvector is mandatory.
- **SECURITY REVIEW OF PROVIDED PSEUDOCODE (page 4):** the example `authorize_tool` sets absent role/group tests to `True` and combines them with `OR`. For role-only or group-only policies that can grant access accidentally. The implementation below uses only *present* predicates, never treats an absent predicate as an authorization match.

## CONFIRMED existing unified system at start

- `src/mcp_server/entra_token_verifier.py`: single-tenant delegated token signature, audience, issuer, tenant, lifetime and `academic.read` validation; production verifier is fail-closed without configuration. No real university-issued token tested.
- `src/mcp_server/team_protected_server.py` and `team_security.py`: six read-only protected academic tools with server-bound student lookup and separate backend authorization. Existing checks are **student-bound**, not complete handout-specific role/group ACL checks.
- `src/agent/ragflow_adapter.py`: read-only synthetic/public dataset allowlist, HTTPS restrictions and source-field validation. It does **not** supply document ACL filtering or post-retrieval document authorization.
- `src/agent/ocr_transcript_handoff.py`: synthetic, non-authoritative provenance validation only. It is **not** an OCR ingestion engine.
- Step 134 checkpoint `29e0315` passed 299 root tests, 1073 AI-agent tests with 1 skipped, and saved synthetic live browser continuity evidence. Those counts do not measure this new role/group authorization feature.

## CONFIRMED Phase 135A changes

1. Added `src/mcp_server/entra_rbac_acl.py`: frozen `SecurityContext`; normalization **only from an already-verified** `AccessToken` under trusted issuer, tenant, audience, expiry and scope consistency checks; missing/unresolved group-overage denies group-gated actions; static `ToolPolicy` with `any`/`all` semantics and default denial for unknown tool names; explicit document ACLs with canonical SHA-256 digest and policy version; in-memory authorized-document candidate prefilter; post-retrieval chunk authorization against the authoritative ACL and digest.
2. Added `tests/test_entra_rbac_acl.py`: five synthetic identities and positive/negative tool/document policy matrices; role-only bypass regression; `ANY_OF`/`ALL_OF`, group overage, expired/bad claims, scope mismatch, cross-tenant access, direct-user ACLs, empty ACL rejection, stale version/hash, unexpected source documents, and model instruction attempting role escalation.
3. The pure contract is currently **isolated**. Existing MCP tool authorization, actual RAGFlow query payloads and chunk-to-LLM assembly have **not** been rewired; security is not overstated.
4. New code and synthetic tests committed on feature branch through `9b40c7dd8db790ba8cd3e8778e0e6ca9636d15bd`. CI at that exact commit reported **7/7 checks successful**: four operating-system/Python pytest jobs (Ubuntu/Windows 3.12/3.13), one Chromium browser job, and two WS1/WS2/WS3 integration checks. Exact test totals for this new test module are not reported here; do not infer counts by adding historical suites.

## WORKING ASSUMPTIONS

- This pure policy layer can be reused by both the MCP enforcement and the retrieval adapter once identity propagation and authoritative ACL storage are designed and audited.
- Local synthetic fixtures are appropriate to test policy logic, but cannot establish a university-approved deployment or real student-data security.
- A metadata-filtering implementation must be aligned with the actual RAGFlow deployment version and vector engine, rather than copy the handout's pseudocode as an API contract.

## OPEN QUESTIONS / requirements not yet satisfied

1. **Trusted identity propagation:** securely inject verified role/group context into tool execution **and** retrieval from the existing Entra/OAuth/session path. Preserve independent student-ID binding.
2. **Group overage:** define an authorized Graph lookup/revalidation strategy, cache lifetime and explicit failure mode; no Graph resolver is present in Phase 135A.
3. **Ingestion:** define allowlisted classifications, trusted source owner, ACL mapping, quarantine, document/chunk metadata transaction, and parity audit before exposing protected datasets.
4. **RAGFlow:** inspect the team's actual server version, index backend, metadata API and supported prefilter; then enforce filter-before-ranking and postretrieval verification. No database/pgvector migration is authorized by this document.
5. **Authorization rules:** define approved UNA-specific Student/Faculty/etc roles/group IDs and scope policy. The handout's HR/Finance/Legal names are **synthetic teaching fixtures**.
6. **Audit:** log allow/deny/filter using identifiers and policy versions, not access tokens or private document text.
7. **Research validation:** run the five identities against the *integrated* tool and retrieval paths, inject unauthorized chunks, test stale ACL/revocation, and capture a real protected-RAG smoke only if the permitted synthetic environment exists.
8. **Academic scheduling:** maintain deterministic planner provenance and proposed-only/no-enrollment semantics; do not let OCR/RAG change Banner-completion authority.

## RECOMMENDED gated next steps

- **135B:** integrate trusted `SecurityContext` and server-owned `ToolPolicy` into the MCP gateway with staged synthetic-token role claims and tests. Keep the original student-owned checks in addition to RBAC. Do not activate incompatible production roles until their identity/app configuration is approved.
- **135C:** implement trusted synthetic document ingestion ACL propagation plus authoritative policy version/hash parity tests. Reject unlabeled or mismatched restricted material.
- **135D:** implement the installed RAGFlow backend's actual metadata pre-filter and independent post-retrieval verifier, then verify no unauthorized content enters agent prompts.
- **135E:** execute the complete five-identity positive/negative integration matrix, isolated live synthetic browser cases, and failure-injection trials. Preserve per-run provenance; do not pool with old heldout2 results.
- **135F:** revise consolidated Master SOT v1.3 and research-paper evaluation using observed outcomes only, then request team/professor review.

**Safety boundary:** Do not make the handout's HR, finance or legal illustrative resources available to this academic scheduling assistant. No real Entra secrets, UNA student records, database writes or enrollment operations were added here.
