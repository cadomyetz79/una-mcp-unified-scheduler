# Phase 135D — Authorized retrieval and Leo policy branch
Date: 2026-11-05 (America/Los_Angeles). Workstream: security/RAG/agent.
Base: 1a9520738d3af57a71913824f548c2ecfa657d93.

## CONFIRMED
AuthorizedKnowledgeRetriever derives document candidates from trusted identity,
dataset/domain allowlists and active ACLs before backend ranking. Empty candidate
sets make no backend call. Each returned chunk must match the authoritative
document, dataset, tenant, full ACL fields, version, hash, source URI and stored
content digest; unexpected chunks are discarded. Catalog changes during retrieval
abort the response. The synthetic backend is lexical ranking, not vector retrieval.

ProtectedRAGFlowBackend sends explicit nonempty document_ids/dataset_ids and asks
for document_metadata. It disables graph, compilation, highlight and TOC expansion.
It is disabled by default until trusted deployment prefilter validation; controlled
MockTransport tests exercise the HTTP contract. No live attestation is configured.

The optional Policy: branch in AuthenticatedSchedulingRunner re-verifies identity
before retrieval, before model access and before response. Only university/student
policy domains can be exposed to Leo. The model receives authorized excerpts and
can select only existing source IDs with no tools. Student output is deterministically
assembled from selected excerpts, not generated eligibility/registration claims.
Invalid model source/tool selections produce no selected evidence. Scheduling
requests continue through protected MCP and deterministic Banner planning.

Local RAGFlow checkout: v0.27.2, a024bea0cd93f39e6652a42bf84dd20c55bc560b.
Configuration defaults to Elasticsearch and image infiniflow/ragflow:v0.27.2.
No running installation was verified: WSL has no RAGFlow listener; Docker is absent
there, and Windows Docker reports its Linux engine pipe unavailable.
Inspected local chunk_api.py and reference_metadata_utils.py: document_ids reaches
the retrieval call; metadata is returned as document_metadata. Child expansion
occurs after retrieval, so deployment-specific pre-ranking guarantees must be
verified rather than inferred from this source inspection alone.

Official API reference documents document_ids and metadata_condition:
https://ragflow.io/docs/http_api_reference (accessed 2026-11-05).
The implementation uses an explicit trusted document list rather than model-created
metadata syntax. It does not claim a protected live RAGFlow deployment.

## Tests and corrections — CONFIRMED
Initial focused run: 33 passed, 1 failed (fixture RAG.Hr differed from required
RAG.HR). Corrected the synthetic fixture; original output retained.
Final focused run: 37 passed. Full root: 420 passed.
Full AI-agent: 1073 passed, 1 skipped.
Evidence: docs/evidence/2026-11-05-135d-*.txt.
Tests check all five classroom identities, actual candidate/result IDs, group
revocation/overage, direct-user ACL, empty candidates, forged metadata/content,
transport failures, source selection escalation and unauthorized text absent from
captured model messages. Phase 135C exact-SHA GitHub workflows all succeeded.

## WORKING ASSUMPTION
Authoritative local content hashes are suitable for the bounded synthetic corpus.
A live ingest adapter must register actual remote chunk IDs/text after approved
ingestion; arbitrary remote chunks cannot be accepted based only on a document ID.

## OPEN QUESTION
Live backend prefilter attestation, remote ingestion metadata parity, credentials,
Graph membership refresh and institutional role assignments remain unavailable.
The old RAGFlowRetriever remains a public/synthetic-only transport contract;
protected Leo uses the new authorized wrapper, never the legacy search method.

## RECOMMENDATION
Keep protected HTTP access disabled until version/backend-specific canary tests
prove pre-ranking restriction and metadata propagation. Preserve exact candidate
IDs and rejected-result cases; do not pool this synthetic matrix with heldout tasks.

CONFIRMED publication check: three synthetic API-key placeholder assignments were flagged; renamed them to explicit example placeholders before publication. No actual credential was involved. Raw failed pytest output retains its original trailing whitespace.
