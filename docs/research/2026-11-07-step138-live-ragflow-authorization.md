# Step 138 A through D — live synthetic RAGFlow authorization

Date: 2026-11-07 America/Los_Angeles. Responsible workstream: unified
security and retrieval integration. Starting SHA:
748df1b7452339d6706a326ada81fc76ce6c2236.
Branch: integration/browser-gateway-20261102.

## CONFIRMED restoration and provenance

The working tree initially contained only untracked historical Phase 135F
evidence. It was preserved. A recovery archive of source, scripts, tests and
documentation was saved outside Git at
/home/mcp_admin/leo-research-evaluations/step138-20261107T162132Z.
team-upstream push URL is DISABLED. PR 3 was OPEN and DRAFT at preflight.
No team repository, n8n configuration, existing corpus or volume was modified.

Compose was rendered using BOTH the original base and existing secure override.
Every effective published port was checked for host_ip 127.0.0.1 before startup.
Web 18080 and API 19380 are the only published lab ports. Supporting ports remain
inside Docker. n8n stayed running on its existing localhost port 5678.
Resources: 16 engine CPUs, 15,598,514,176 bytes engine memory, 4 GiB WSL swap,
approximately 947 GiB free WSL disk at preflight. No OOM flag or container
restart was observed during the recorded trial.

Images: infiniflow/ragflow:v0.27.2, elasticsearch:8.11.3, mysql:8.0.40,
valkey/valkey:8, pgsty/silo:RELEASE.2026-08-06T00-00-00Z.
Exact image IDs, health, memory and model digests are in
docs/evidence/2026-11-07-138-environment.json.
RAGFlow source SHA: a024bea0cd93f39e6652a42bf84dd20c55bc560b.
Initial API connection resets resolved after initialization; web returned 200,
then the API returned its authentication-required code. This was startup
readiness, not a reason to bypass authentication. Container log dates use a
different timezone; this report uses the client date.

A new local synthetic account was legitimately registered via /api/v1/users.
An API credential was created through authenticated /system/tokens. Credentials
are outside the repository in a mode-0600 file inside a mode-0700 directory,
with a local ignore rule. No credentials or raw authentication responses are
research evidence.

## CONFIRMED ingestion and retrieval

The container can reach the existing local Ollama service through
host.docker.internal:11434. Installed nomic-embed-text and configured the Ollama
embedding provider using authenticated API operations; no paid API was used.
Six synthetic plain-text documents were uploaded, ACL metadata was set before
parse, and all six reached DONE with one actual embedded/indexed chunk each.
A second new corpus reproduced those steps using scripts/ragflow_lab_ingest.py.
Original documents and trial artifacts were retained.

The test corpus deliberately puts six role variants into ONE university-policy
dataset to test document-level filtering within a dataset. Its HR/Finance/Legal
texts are artificial canaries, not institutional documents or approved domain
classification. Leo's resulting registry includes only public and Student
documents, even if a student identity has additional HR or Legal privileges.

The actual naive parser prepended one newline to these text files. Remote
chunk binding checks this exact trusted transformation, document/dataset IDs,
every ACL/provenance field, policy version type and source text before atomically
registering remote IDs. Arbitrary remote text is never made authoritative.
A partial or failed binding leaves the previous registry unchanged.

RAGFlow returns document_metadata by document-level enrichment. Observed response
parity is confirmed; this does NOT claim that every vector record stores a
duplicate complete ACL. Authorization is server-derived explicit document IDs,
plus independent local authoritative metadata/content checks after retrieval.

## CONFIRMED pre-ranking canary

Query: Quantum scholarship award eligibility.
With knn_top_k=1, knn_num_candidates=1, rerank_candidates_count=1,
page_size=1, vector_similarity_weight=1, similarity_threshold=0:
- Unrestricted laboratory query returned the highly relevant Legal decoy.
- Public-only document_ids returned the lower-scoring public document.
- Student-only document_ids returned the lower-scoring Student document.
All were real authenticated HTTP queries to Elasticsearch-backed RAGFlow.
This is behavioral evidence that the tested explicit document allowlist affects
candidate selection before the bounded top-1 result; it is not merely removing
the forbidden top result afterward. It is not a universal proof for all engines,
versions, parser settings or search expansion features.

The factory repeats the canary at EACH opt-in startup and binds verified chunks
before enabling the existing ProtectedRAGFlowBackend. It then tests the default
adapter settings through AuthorizedKnowledgeRetriever for all five roles:
each retrieves exactly public plus its own document. Refreshed Legal identities
without the required role/group, and group-overage identities, retrieve public
only. A foreign synthetic tenant receives an empty set. Actual document/chunk
IDs, requests, ACL metadata and responses are preserved in
docs/evidence/2026-11-07-138-canary-final.json.
The unrestricted decoy query is a test-only measurement and never enters Leo.

Default protected HTTP retrieval remains disabled. src/agent/ragflow_lab.py is
an explicit synthetic loopback factory, not production activation. It refuses
other URLs, mismatched tenant/configuration, nonprivate credential files,
canary failures, content mutations and metadata mismatches. The backend flags
disable knowledge compilation, KG and TOC expansion; parent/child parsing was
off in the recorded corpus.

## CONFIRMED implementation and tests

Changed: src/agent/secure_ingestion.py (atomic remote binding);
src/agent/ragflow_lab.py (runtime gate and academic-only corpus);
scripts/ragflow_lab_ingest.py; scripts/ragflow_live_canary.py;
tests/test_remote_chunk_binding.py; tests/test_ragflow_lab.py.

Final root: 454 passed. AI-agent: 1073 passed, 1 skipped.
Protected MCP/retrieval security selection: 112 passed.
These suites overlap; do not sum them or call them model accuracy.
Initial root trial: 448 passed, 5 failed, 1 warning because new tests used an
uninstalled pytest async plugin. Corrected the harness to the repository's
asyncio.run convention; no application guard or assertion was relaxed.
Intermediate root: 453 passed before the extra-role academic-scope regression.
Original failed output remains docs/evidence/2026-11-07-138-root.txt.
Final outputs use root-verified.txt, security-verified.txt and agent.txt.
Earlier 62-test focus and 22-test binding/gate runs are separate overlapping
checks. Canary runs are live demonstrations, not pytest counts.

## CONFIRMED teammate attribution

Read-only review checkout ite499-shared-review remains at
7ef1b01501879c34008b50aeb0e23a7f9e608465 and unmodified.
Its Haystack component connects tenant + hashed ACL metadata predicates directly
to BM25 retrieval. The team's 11-test result is prior evidence, NOT rerun or
combined with these measurements. Its development authentication and OpenAI
generator are not imported into this implementation. The design principle of
filter-before-prompt is shared; the unified server-owned ACL schema, ANY/ALL
semantics, signed identity path and RAGFlow adapter remain independently
implemented. Hashed ACL keys are not interchangeable with this registry.

## WORKING ASSUMPTIONS

An exact, small synthetic corpus is suitable for detecting common prefilter
regressions; larger unseen corpora and parser variants need separate testing.
Loopback and a dedicated private lab account constrain this demonstration.

## OPEN QUESTIONS

No live UNA Entra, Graph membership refresh, production Banner or institutional
ACL approval is established. Current unexpired tokens do not imply immediate
directory revocation. No distributed/durable authorization registry, continuous
backend attestation, automatic remote ACL synchronization, general OCR or
production ingestion is implemented. A compromised privileged RAGFlow service
or host is outside this limited canary's proof. Missing or changed response
metadata/content is still rejected by the existing post-retrieval boundary.

## RECOMMENDATIONS

Keep production activation disabled. Retain explicit corpus configuration and
run fresh canaries after engine, parser, model or deployment changes. Expand
adversarial datasets and approve identity/ACL ownership before institutional use.
Use the companion Step 138 runbook and browser closeout for reproduction.
Final commit IDs are indexed in the closeout; a commit cannot contain its own SHA.
