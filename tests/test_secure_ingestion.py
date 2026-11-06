"""Synthetic ingestion/parity and atomic failure regressions."""
from dataclasses import replace
import pytest
from src.agent.secure_ingestion import DocumentRecord, SyntheticDocumentStore
from src.mcp_server.entra_rbac_acl import DocumentACL, AuthorizationDenied


def fixture():
    store = SyntheticDocumentStore({"student-data": "student-policy"})
    acl = DocumentACL(
        "student-guide", "tenant-a", "restricted", "student-policy", "synthetic-restricted",
        allowed_roles=frozenset({"RAG.Student"}), allowed_users=frozenset({"student-a"}), mode="all",
    )
    return store, DocumentRecord(acl, "student-data", "synthetic://student-guide/segment-1")


def test_acl_validated_before_parser():
    store, doc = fixture()
    called = []
    with pytest.raises(AuthorizationDenied):
        store.ingest(replace(doc, dataset_id="unapproved"), b"private", parser=lambda raw: called.append(raw))
    assert called == []
    assert store.snapshot()[1:] == ({}, {})


def test_every_chunk_inherits_full_acl_and_provenance():
    store, doc = fixture()
    chunks = store.ingest(doc, b"x" * 2500)
    assert len(chunks) == 3
    for chunk in chunks:
        assert chunk.document == doc
        assert chunk.metadata["acl_hash"] == doc.acl.acl_hash
        assert chunk.metadata["policy_version"] == 1
        assert chunk.metadata["allowed_users"] == ["student-a"]
        assert chunk.metadata["allowed_roles"] == ["RAG.Student"]
        assert chunk.metadata["source_uri"] == doc.source_uri


@pytest.mark.parametrize("parsed", [[], ["ok", ""], ["x"*1201], ["ok", None], ("wrong",)])
def test_partial_write_failure_is_atomic(parsed):
    store, doc = fixture()
    original = store.ingest(doc, b"original")
    before = store.snapshot()
    with pytest.raises(ValueError):
        store.ingest(doc, b"replacement", parser=lambda raw: parsed)
    assert store.snapshot() == before
    assert tuple(store.snapshot()[2].values()) == original


def test_policy_update_invalidates_chunks_and_old_ingestion():
    store, doc = fixture()
    store.ingest(doc, b"original")
    new = store.update_policy(replace(doc.acl, policy_version=2, allowed_users=frozenset({"student-b"})))
    assert not store.snapshot()[2]
    with pytest.raises(AuthorizationDenied):
        store.ingest(doc, b"stale")
    with pytest.raises(AuthorizationDenied):
        store.update_policy(doc.acl)
    assert store.ingest(new, b"new")[0].metadata["policy_version"] == 2


def test_policy_change_during_parse_aborts_without_partial_commit():
    store, doc = fixture()
    store.ingest(doc, b"original")
    def parser(raw):
        store.revoke(doc.acl.document_id)
        return ["must not commit"]
    with pytest.raises(AuthorizationDenied):
        store.ingest(doc, b"replacement", parser=parser)
    assert store.snapshot()[1][doc.acl.document_id].revoked
    assert not store.snapshot()[2]


def test_mixed_permission_segments_remain_separate():
    store, doc = fixture()
    other = replace(doc, acl=replace(doc.acl, document_id="segment-2", allowed_users=frozenset({"student-b"})),
                    source_uri="synthetic://student-guide/segment-2")
    a = store.ingest(doc, b"A")[0]
    b = store.ingest(other, b"B")[0]
    assert a.metadata["acl_hash"] != b.metadata["acl_hash"]
    assert a.metadata["allowed_users"] != b.metadata["allowed_users"]


@pytest.mark.parametrize("changes", [
    {"source_uri": "https://unapproved.invalid/real-record"},
    {"acl": None},
    {"dataset_id": "bad; DROP TABLE documents"},
])
def test_invalid_source_metadata_rejected(changes):
    _, doc = fixture()
    with pytest.raises(ValueError):
        replace(doc, **changes)
