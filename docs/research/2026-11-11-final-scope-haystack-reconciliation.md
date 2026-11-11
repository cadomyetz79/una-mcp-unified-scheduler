# Step 145 — final research scope and Haystack evidence reconciliation

Date: 2026-11-11 (America/Chicago). Status: RESEARCH RECONCILIATION; NOT an integration or test run.

## Decision
The project integrator reports that Haystack is the team's final RAG platform and that access to real UNA Banner and Entra identity services will not be granted. Historical research question is preserved, while experimental outcomes use synthetic Mock Banner and simulated Entra-oriented identity verification.

## Inspectable evidence and limits
1. Unified repo `cadomyetz79/una-mcp-unified-scheduler`, branch `integration/browser-gateway-20261102`, baseline `fb1500357c2b3d3de37f1ae46097a2aeb7950dc0`: previously verified five-turn live Leo+**RAGFlow** browser trial, 458 root passed, 1,073 agent passed/1 skipped, seven GitHub CI checks passed. The RAGFlow server uses actual synthetic HTTP retrieval and prefilter canary, not Haystack.
2. Teammate repo `devink727/ite499-shared`: current connected GitHub access returned HTTP 404 for metadata, README, commit list and repository URL as of this update. Do not assert an up-to-date tree or current test results.
3. Local archival source review `Pasted text(20261106-042944).txt` at teammate SHA `7ef1b01` showed Haystack 3.2.0, FastAPI POST /query, `pipeline.py` with InMemoryBM25Retriever + InMemoryDocumentStore + ChatPromptBuilder + OpenAIChatGenerator(gpt-4o-mini), and `security_policy.py` deriving tenant/ACL filters from *mock* identity claims. `test_harness.py` defined eleven tests on role, group, user and cross-tenant restrictions and malformed-claim refusal. These tests were inspected, not rerun in this update; no end-to-end Haystack+Leo/browser result is established.
4. Professor handout `Entra_ID_MCP_RAG_Authorization_Student_Handout.docx` is a design and testing reference for signed token validation, security context, MCP RBAC and pre-/post-retrieval protection; no university Entra tenant or real student data connected.

## Paper claims and labeling
- **Evidence A (unified scheduling):** tested read-only synthetic MCP+agent+Mock Banner scheduling; no enrollment; deterministic constraints; synthetic login and security tests. Use exact observed denominators; do not call test counts a model accuracy score.
- **Evidence B (separate Haystack):** source-inspected BM25 metadata-filter/RAG service, with 11 named unit test methods; integration into final Leo and latest runtime outcomes **UNVERIFIED**.
- **Evidence C (historical optional RAGFlow):** actually demonstrated live synthetic RAGFlow retrieval and browser session; **NOT** a Haystack result. Include only as clearly labeled historical exploration, if relevant to methods.
- **Negative:** no live SSO, production Banner, FERPA-approved deployment, real enrollment action, or authorized university policy document corpus.

## Next gates
Obtain current Haystack source archive or authorized GitHub access, rerun and document the test suite, confirm source/role contribution ownership and final manuscript requirements. Do not overwrite archival materials or turn unverified connections into completed features.
