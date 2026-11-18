"""Trusted prefilter -> backend -> authoritative chunk verification.

The local backend is a synthetic lexical simulator, not vector-search evidence.
HTTP protected retrieval remains disabled without trusted deployment validation.
"""
import hashlib
import logging
import json
import httpx2
from src.agent.knowledge_retrieval import KnowledgeHit
from src.agent.ragflow_adapter import RAGFlowRetriever
from src.mcp_server.entra_rbac_acl import SecurityContext, AuthorizationDenied, document_is_authorized


class SyntheticPrefilterBackend:
    prefilter_verified = True

    def __init__(self, store):
        self.store = store
        self.last_candidates = ()

    async def search_documents(self, query, dataset_ids, document_ids, limit):
        if not document_ids:
            raise AuthorizationDenied("Empty document candidates.")
        _, _, chunks = self.store.snapshot()
        # This filter runs before the synthetic relevance sort.
        candidates = [c for c in chunks.values()
                      if c.document.dataset_id in dataset_ids
                      and c.document.acl.document_id in document_ids]
        self.last_candidates = tuple(c.chunk_id for c in candidates)
        ranked = sorted(candidates, key=lambda c: (-sum(w in c.text.lower() for w in query.lower().split()), c.chunk_id))
        return [
            {"id": c.chunk_id, "document_id": c.document.acl.document_id,
             "dataset_id": c.document.dataset_id, "content": c.text,
             "document_metadata": c.metadata}
            for c in ranked[:limit]
        ]


class ProtectedRAGFlowBackend:
    """Document-ID API adapter; deployment attestation is server-owned.

    False by default. Source/API documentation alone is insufficient to enable.
    Tests may attest a controlled MockTransport; no live attestation ships here.
    """
    def __init__(self, connection: RAGFlowRetriever, *, prefilter_verified=False):
        if type(prefilter_verified) is not bool:
            raise ValueError("Trusted boolean capability required.")
        self.connection = connection
        self.prefilter_verified = prefilter_verified

    async def search_documents(self, query, dataset_ids, document_ids, limit):
        if (not self.prefilter_verified or not document_ids
            or not set(dataset_ids).issubset(self.connection.dataset_ids)):
            raise AuthorizationDenied("Verified document prefilter required.")
        payload = {
            "question": query, "dataset_ids": list(dataset_ids),
            "document_ids": list(document_ids), "page": 1, "page_size": limit,
            "use_kg": False, "toc_enhance": False,
            "include_knowledge_compilation": False, "highlight": False,
            "reference_metadata": {"include": True},
        }
        async def request(client):
            try:
                response = await client.post(
                    self.connection.endpoint,
                    headers={"Authorization": f"Bearer {self.connection.api_key}"},
                    json=payload, follow_redirects=False,
                )
                if response.status_code != 200 or len(response.content) > 1_000_000:
                    raise ValueError("Rejected retrieval response.")
                data = response.json()
                if (type(data) is not dict or type(data.get("code")) is not int
                    or data["code"] != 0 or type(data.get("data")) is not dict
                    or type(data["data"].get("chunks")) is not list):
                    raise ValueError("Invalid retrieval response.")
                return data["data"]["chunks"]
            except (httpx2.HTTPError, ValueError):
                raise RuntimeError("Protected retrieval unavailable.") from None
        if self.connection.client is not None:
            return await request(self.connection.client)
        async with httpx2.AsyncClient(timeout=10, follow_redirects=False, trust_env=False) as client:
            return await request(client)


class AuthorizedKnowledgeRetriever:
    def __init__(self, store, backend, *, dataset_ids, domains):
        if (not dataset_ids or not domains
            or not set(dataset_ids).issubset(store.dataset_domains)
            or any(store.dataset_domains[d] not in domains for d in dataset_ids)):
            raise ValueError("Trusted dataset/domain allowlist required.")
        self.store, self.backend = store, backend
        self.dataset_ids, self.domains = frozenset(dataset_ids), frozenset(domains)

    async def search_for(self, user, query, limit=3):
        if type(user) is not SecurityContext or "rag.query" not in user.scopes:
            raise AuthorizationDenied("Knowledge access denied.")
        if (type(query) is not str or not query.strip() or len(query) > 500
            or any(ord(c) < 32 for c in query)
            or type(limit) is not int or not 1 <= limit <= 5):
            raise ValueError("Invalid knowledge query.")
        if getattr(self.backend, "prefilter_verified", False) is not True:
            raise AuthorizationDenied("Retrieval prefilter is not verified.")
        revision, documents, _ = self.store.snapshot()
        eligible = {
            key: doc for key, doc in documents.items()
            if not doc.revoked and doc.dataset_id in self.dataset_ids
            and doc.acl.data_domain in self.domains and document_is_authorized(doc.acl, user)
        }
        if not eligible:
            logging.getLogger(__name__).info("retrieval decision=empty")
            return []
        if len(eligible) > 256:
            raise AuthorizationDenied("Candidate bound exceeded.")
        raw = await self.backend.search_documents(
            query.strip(), tuple(sorted({d.dataset_id for d in eligible.values()})),
            tuple(sorted(eligible)), limit,
        )
        current_revision, current_docs, chunks = self.store.snapshot()
        if current_revision != revision:
            raise AuthorizationDenied("Retrieval policy snapshot changed.")
        if type(raw) is not list or len(raw) > 100:
            raise ValueError("Invalid retrieval result bound.")
        hits, seen = [], set()
        for row in raw:
            if type(row) is not dict:
                continue
            cid, did, dataset = row.get("id"), row.get("document_id"), row.get("dataset_id")
            if any(type(v) is not str for v in (cid, did, dataset)):
                continue
            chunk, doc = chunks.get(cid), current_docs.get(did)
            metadata, content = row.get("document_metadata"), row.get("content")
            if (did not in eligible or doc is None or doc.revoked or chunk is None
                or chunk.document != doc or dataset != doc.dataset_id
                or not document_is_authorized(doc.acl, user)
                or type(metadata) is not dict or type(metadata.get("policy_version")) is not int
                or type(content) is not str or len(content) > 1200):
                continue
            expected = chunk.metadata
            if any(metadata.get(k) != v for k,v in expected.items() if k != "content_hash"):
                continue
            if hashlib.sha256(content.encode("utf-8")).hexdigest() != chunk.content_hash:
                continue
            if cid not in seen:
                seen.add(cid)
                hits.append(KnowledgeHit(
                    source_id=f"{dataset}/{did}/{cid}", title=did, excerpt=content,
                ))
        logging.getLogger(__name__).info("retrieval decision=verified count=%d", len(hits[:limit]))
        return hits[:limit]
