"""Remote ingestion cannot convert arbitrary HTTP content into trusted evidence."""
from copy import deepcopy
import hashlib
import pytest
from src.agent.secure_ingestion import SyntheticDocumentStore, DocumentRecord, ChunkRecord
from src.mcp_server.entra_rbac_acl import DocumentACL, AuthorizationDenied


def fixture():
    store = SyntheticDocumentStore({"dataset": "university-policy"})
    doc = DocumentRecord(DocumentACL("document", "tenant", "public", "university-policy",
                                     "synthetic-public"), "dataset", "synthetic://test/policy")
    text = "\nSynthetic local policy."
    chunk = ChunkRecord("remote123", doc, text, hashlib.sha256(text.encode()).hexdigest())
    row = {"id": chunk.chunk_id, "document_id": "document", "dataset_id": "dataset",
           "content": text, "document_metadata": chunk.metadata}
    return store, doc, text, row


def test_remote_ids_bound_only_after_exact_parity():
    store, doc, text, row = fixture()
    chunks = store.bind_remote_chunks(doc, [text], [row])
    assert store.snapshot()[2]["remote123"] == chunks[0]
    assert chunks[0].content_hash == hashlib.sha256(text.encode()).hexdigest()


@pytest.mark.parametrize("field,value", [
    ("id", "../bad"), ("document_id", "other"), ("dataset_id", "other"),
    ("content", "Forged evidence"), ("document_metadata", {}),
])
def test_bad_binding_is_atomic(field, value):
    store, doc, text, row = fixture()
    row[field] = value
    before = store.snapshot()
    with pytest.raises(AuthorizationDenied):
        store.bind_remote_chunks(doc, [text], [row])
    assert store.snapshot() == before


@pytest.mark.parametrize("field,value", [
    ("policy_version", True), ("acl_hash", "forged"), ("tenant_id", "other"),
    ("allowed_roles", ["RAG.Legal"]),
])
def test_metadata_mutation_rejected(field, value):
    store, doc, text, row = fixture()
    row["document_metadata"][field] = value
    with pytest.raises(AuthorizationDenied):
        store.bind_remote_chunks(doc, [text], [row])


def test_duplicate_chunk_and_incomplete_binding_rejected():
    store, doc, text, row = fixture()
    with pytest.raises(AuthorizationDenied):
        store.bind_remote_chunks(doc, [text, text], [row, deepcopy(row)])
    with pytest.raises(ValueError):
        store.bind_remote_chunks(doc, [text], [])
    assert store.snapshot()[1:] == ({}, {})


def test_failed_rebind_preserves_prior_verified_content():
    store, doc, text, row = fixture()
    store.bind_remote_chunks(doc, [text], [row])
    before = store.snapshot()
    row["content"] = "untrusted replacement"
    with pytest.raises(AuthorizationDenied):
        store.bind_remote_chunks(doc, [text], [row])
    assert store.snapshot() == before
