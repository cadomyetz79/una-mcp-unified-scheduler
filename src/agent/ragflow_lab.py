"""Opt-in synthetic loopback RAGFlow lab. Never enables production retrieval.

The server-owned manifest records locally authored source text and ACLs.
Each startup reruns an adversarial top-1 canary against the live backend.
No cached boolean or model-supplied setting can enable this factory.
"""
import json
import os
from pathlib import Path
import httpx2
from src.agent.secure_ingestion import SyntheticDocumentStore, DocumentRecord
from src.agent.ragflow_adapter import RAGFlowRetriever
from src.agent.authorized_retrieval import AuthorizedKnowledgeRetriever, ProtectedRAGFlowBackend
from src.mcp_server.entra_rbac_acl import DocumentACL, SecurityContext, AuthorizationDenied

NAMES = {"public", "student", "faculty", "hr", "finance", "legal"}


def load_lab_files(manifest_path, credential_path, expected_tenant):
    manifest_path, credential_path = Path(manifest_path), Path(credential_path)
    if credential_path.is_symlink() or (os.name != "nt" and credential_path.stat().st_mode & 0o077):
        raise PermissionError("Lab credential file must be private.")
    if manifest_path.stat().st_size > 100_000 or credential_path.stat().st_size > 16_384:
        raise ValueError("Lab configuration exceeds bounds.")
    manifest = json.loads(manifest_path.read_text())
    credentials = json.loads(credential_path.read_text())
    if (manifest.get("schema_version") != "synthetic-ragflow-lab-v1"
        or manifest.get("tenant_id") != expected_tenant
        or manifest.get("base_url") != "http://127.0.0.1:19380"
        or type(manifest.get("documents")) is not list
        or len(manifest["documents"]) != 6
        or {d.get("name") for d in manifest["documents"]} != NAMES):
        raise ValueError("Explicit synthetic loopback manifest required.")
    return manifest, credentials["api_key"]


async def verified_lab_retriever(manifest_path, credential_path, *, expected_tenant):
    manifest, credential = load_lab_files(manifest_path, credential_path, expected_tenant)
    dataset = manifest["dataset_id"]
    store = SyntheticDocumentStore({dataset: "university-policy"})
    docs = {}
    for item in manifest["documents"]:
        meta = item["metadata"]
        acl = DocumentACL(
            item["id"], expected_tenant, meta["visibility"], meta["data_domain"],
            meta["classification"], allowed_roles=frozenset(meta["allowed_roles"]),
            allowed_groups=frozenset(meta["allowed_groups"]), allowed_users=frozenset(meta["allowed_users"]),
            mode=meta["mode"], policy_version=meta["policy_version"],
        )
        name = item["name"]
        role = "RAG.HR" if name == "hr" else "RAG." + name.capitalize()
        group = {"hr": "hr-confidential", "legal": "legal-privileged"}.get(name)
        if (acl.visibility != ("public" if name == "public" else "restricted")
            or acl.allowed_roles != (frozenset() if name == "public" else frozenset({role}))
            or acl.allowed_groups != (frozenset({group}) if group else frozenset())
            or acl.allowed_users or acl.mode != "all" or acl.acl_hash != meta["acl_hash"]
            or type(item["text"]) is not str or not 1 <= len(item["text"]) <= 1199):
            raise AuthorizationDenied("Unexpected synthetic corpus policy.")
        docs[name] = (item, DocumentRecord(acl, dataset, meta["source_uri"]))
    if len({d[0]["id"] for d in docs.values()}) != 6:
        raise ValueError("Duplicate document IDs.")
    connection = RAGFlowRetriever(base_url=manifest["base_url"], api_key=credential, dataset_ids=[dataset])
    base = {
        "dataset_ids": [dataset], "question": "Quantum scholarship award eligibility",
        "page": 1, "page_size": 1, "knn_top_k": 1, "knn_num_candidates": 1,
        "rerank_candidates_count": 1, "similarity_threshold": 0, "vector_similarity_weight": 1,
        "use_kg": False, "toc_enhance": False, "include_knowledge_compilation": False,
        "highlight": False, "reference_metadata": {"include": True},
    }
    evidence = {"synthetic_only": True, "live_ragflow": True, "passed": False,
                "dataset_id": dataset, "canary": [], "matrix": []}
    async with httpx2.AsyncClient(timeout=60, trust_env=False, follow_redirects=False) as client:
        async def query(payload):
            try:
                response = await client.post(connection.endpoint,
                    headers={"Authorization": "Bearer " + credential}, json=payload)
                if response.status_code != 200 or len(response.content) > 1_000_000:
                    raise ValueError()
                value = response.json()
                if type(value) is not dict or type(value.get("code")) is not int or value["code"] != 0:
                    raise ValueError()
                rows = value["data"]["chunks"]
                if type(rows) is not list or len(rows) > 100:
                    raise ValueError()
                return rows
            except (httpx2.HTTPError, ValueError, KeyError, TypeError):
                raise RuntimeError("Live RAGFlow canary unavailable.") from None
        # An unrestricted *test-only* query must select the forbidden decoy.
        # It never enters an assistant prompt or the authorized retriever.
        for label, name in [("unrestricted", None), ("public_only", "public"), ("student_only", "student")]:
            payload = dict(base)
            if name:
                payload["document_ids"] = [docs[name][0]["id"]]
            rows = await query(payload)
            expected = docs[name or "legal"][0]["id"]
            if len(rows) != 1 or rows[0].get("document_id") != expected:
                raise AuthorizationDenied("Live pre-ranking canary failed.")
            evidence["canary"].append({"case": label, "request": payload, "returned": rows})
        # Bind exact authored content (the observed naive text parser adds one newline).
        # Do not accept arbitrary parser transformations or remote text as authority.
        for name, (item, doc) in docs.items():
            payload = dict(base, document_ids=[item["id"]], page_size=5,
                           knn_top_k=5, knn_num_candidates=5, rerank_candidates_count=5)
            rows = await query(payload)
            store.bind_remote_chunks(doc, ["\n" + item["text"]], rows)
    backend = ProtectedRAGFlowBackend(connection, prefilter_verified=True)
    retriever = AuthorizedKnowledgeRetriever(store, backend, dataset_ids={dataset}, domains={"university-policy"})
    for name in sorted(NAMES - {"public"}):
        role = "RAG.HR" if name == "hr" else "RAG." + name.capitalize()
        group = {"hr": "hr-confidential", "legal": "legal-privileged"}.get(name)
        identity = SecurityContext(expected_tenant, "synthetic-" + name, roles=frozenset({role}),
            groups=frozenset({group}) if group else frozenset(), scopes=frozenset({"rag.query"}))
        hits = await retriever.search_for(identity, "Synthetic policy guidance", 5)
        actual = sorted(h.source_id.split("/")[1] for h in hits)
        allowed = sorted([docs["public"][0]["id"], docs[name][0]["id"]])
        if actual != allowed:
            raise AuthorizationDenied("Live identity matrix did not retrieve exactly the authorized documents.")
        evidence["matrix"].append({"role": role, "authorized_documents": allowed,
            "verified_sources": [h.source_id for h in hits]})
    evidence["revocation"] = []
    for case, role, groups, complete in [
        ("legal_group_removed", "RAG.Legal", frozenset(), True),
        ("legal_role_removed", "", frozenset({"legal-privileged"}), True),
        ("legal_group_overage", "RAG.Legal", frozenset({"legal-privileged"}), False),
    ]:
        identity = SecurityContext(expected_tenant, "synthetic-legal",
            roles=frozenset({role}) if role else frozenset(), groups=groups,
            scopes=frozenset({"rag.query"}), groups_complete=complete)
        hits = await retriever.search_for(identity, "Synthetic policy guidance", 5)
        if [h.source_id.split("/")[1] for h in hits] != [docs["public"][0]["id"]]:
            raise AuthorizationDenied("Live refreshed-identity restriction failed.")
        evidence["revocation"].append({"case": case, "verified_sources": [h.source_id for h in hits]})
    foreign = SecurityContext("other-synthetic-tenant", "synthetic-user", scopes=frozenset({"rag.query"}))
    if await retriever.search_for(foreign, "policy"):
        raise AuthorizationDenied("Tenant isolation failed.")
    evidence["cross_tenant_empty"] = True
    evidence["passed"] = True
    # The five-role corpus is a security canary, not Leo's knowledge scope.
    # Even a student with additional Legal/HR roles must not expose those
    # teaching documents through the academic assistant.
    academic_store = SyntheticDocumentStore({dataset: "university-policy"})
    _, _, verified_chunks = store.snapshot()
    for name in ("public", "student"):
        item, doc = docs[name]
        chunks = [c for c in verified_chunks.values() if c.document == doc]
        rows = [{"id": c.chunk_id, "document_id": item["id"], "dataset_id": dataset,
                 "content": c.text, "document_metadata": c.metadata} for c in chunks]
        academic_store.bind_remote_chunks(doc, ["\n" + item["text"]], rows)
    academic_retriever = AuthorizedKnowledgeRetriever(
        academic_store, backend, dataset_ids={dataset}, domains={"university-policy"})
    evidence["leo_document_allowlist"] = sorted(academic_store.snapshot()[1])
    return academic_retriever, evidence
