"""Offline tests of explicit lab enablement; never claim live retrieval."""
import asyncio
import json
from pathlib import Path
import pytest
import httpx2
from src.agent import ragflow_lab as lab
from src.agent.secure_ingestion import DocumentRecord, ChunkRecord
from src.mcp_server.entra_rbac_acl import DocumentACL, AuthorizationDenied


def config(tmp_path):
    documents = []
    for name in sorted(lab.NAMES):
        role = "RAG.HR" if name == "hr" else "RAG." + name.capitalize()
        group = {"hr": "hr-confidential", "legal": "legal-privileged"}.get(name)
        acl = DocumentACL(name, "tenant", "public" if name == "public" else "restricted",
            "university-policy", "synthetic-public" if name == "public" else "synthetic-restricted",
            allowed_roles=frozenset() if name == "public" else frozenset({role}),
            allowed_groups=frozenset({group}) if group else frozenset(), mode="all")
        doc = DocumentRecord(acl, "dataset", "synthetic://canary/" + name)
        documents.append({"name": name, "id": name, "text": "Synthetic " + name,
            "metadata": ChunkRecord("pending", doc, "", "").metadata})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": "synthetic-ragflow-lab-v1",
        "base_url": "http://127.0.0.1:19380", "tenant_id": "tenant", "dataset_id": "dataset",
        "documents": documents}))
    credentials = tmp_path / "private.json"
    credentials.write_text(json.dumps({"api_key": "example-lab-key"}))
    credentials.chmod(0o600)
    return manifest, credentials


@pytest.mark.parametrize("field,value", [
    ("base_url", "http://public.example.invalid"), ("tenant_id", "other"),
    ("schema_version", "unknown"), ("documents", []),
])
def test_lab_configuration_fails_closed(tmp_path, field, value):
    manifest, credentials = config(tmp_path)
    data = json.loads(manifest.read_text())
    data[field] = value
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        lab.load_lab_files(manifest, credentials, "tenant")


@pytest.mark.parametrize("failure", ["empty", "forbidden", "outage", "malformed", "forged_text"])
def test_live_factory_cannot_enable_after_failed_canary(tmp_path, monkeypatch, failure):
    manifest, credentials = config(tmp_path)
    data = json.loads(manifest.read_text())
    by_id = {d["id"]: d for d in data["documents"]}
    def handle(request):
        if failure == "outage":
            return httpx2.Response(503)
        if failure == "malformed":
            return httpx2.Response(200, json={"code": True, "data": {}})
        payload = json.loads(request.content)
        did = payload.get("document_ids", ["legal"])[0]
        if failure == "forbidden":
            did = "legal"
        d = by_id[did]
        rows = [] if failure == "empty" else [{"id": did + "-chunk", "document_id": did,
            "dataset_id": "dataset", "content": "forged" if failure == "forged_text" else "\n" + d["text"],
            "document_metadata": d["metadata"]}]
        return httpx2.Response(200, json={"code": 0, "data": {"chunks": rows}})
    original = httpx2.AsyncClient
    monkeypatch.setattr(lab.httpx2, "AsyncClient", lambda **kwargs:
        original(transport=httpx2.MockTransport(handle), **kwargs))
    with pytest.raises((AuthorizationDenied, RuntimeError)):
        asyncio.run(lab.verified_lab_retriever(manifest, credentials, expected_tenant="tenant"))


def test_successful_canary_still_limits_leo_to_academic_documents(tmp_path, monkeypatch):
    manifest, credentials = config(tmp_path)
    data = json.loads(manifest.read_text())
    docs = {d["id"]: d for d in data["documents"]}
    def handle(request):
        query = json.loads(request.content)
        ids = query.get("document_ids", ["legal"])
        rows = [{"id": did + "-chunk", "document_id": did, "dataset_id": "dataset",
                 "content": "\n" + docs[did]["text"], "document_metadata": docs[did]["metadata"]}
                for did in ids]
        return httpx2.Response(200, json={"code": 0, "data": {"chunks": rows}})
    original = httpx2.AsyncClient
    monkeypatch.setattr(lab.httpx2, "AsyncClient", lambda **kwargs:
        original(transport=httpx2.MockTransport(handle), **kwargs))
    async def exercise():
        retriever, evidence = await lab.verified_lab_retriever(manifest, credentials, expected_tenant="tenant")
        assert evidence["passed"]
        assert set(retriever.store.snapshot()[1]) == {"public", "student"}
        identity = lab.SecurityContext("tenant", "student-with-extra-roles",
            roles=frozenset({"RAG.Student", "RAG.Legal", "RAG.HR"}),
            groups=frozenset({"legal-privileged", "hr-confidential"}), scopes=frozenset({"rag.query"}))
        hits = await retriever.search_for(identity, "policy")
        assert {h.source_id.split("/")[1] for h in hits} == {"public", "student"}
    asyncio.run(exercise())
