"""Atomic, in-memory synthetic ingestion. No production corpus writes or OCR.

Each input is one explicitly classified security segment. Different permission
segments must be separate document IDs; the parser cannot broaden their ACLs.
"""
from dataclasses import dataclass, replace
import hashlib
import logging
import re
import threading
from types import MappingProxyType

from src.mcp_server.entra_rbac_acl import DocumentACL, AuthorizationDenied

DOMAINS = frozenset({"university-policy", "student-policy", "faculty-policy", "hr", "finance", "legal"})
CLASSIFICATIONS = frozenset({"synthetic", "synthetic-public", "synthetic-restricted"})
_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")


@dataclass(frozen=True)
class DocumentRecord:
    acl: DocumentACL
    dataset_id: str
    source_uri: str
    revoked: bool = False

    def __post_init__(self):
        if type(self.acl) is not DocumentACL:
            raise ValueError("Validated source ACL required.")
        if (type(self.dataset_id) is not str or not _ID.fullmatch(self.dataset_id)
            or not _ID.fullmatch(self.acl.document_id)
            or self.acl.data_domain not in DOMAINS
            or self.acl.classification not in CLASSIFICATIONS
            or type(self.source_uri) is not str
            or not re.fullmatch(r"synthetic://[A-Za-z0-9_./-]{1,200}", self.source_uri)
            or type(self.revoked) is not bool):
            raise ValueError("Approved synthetic source metadata required.")
        if self.acl.classification == "synthetic-restricted" and self.acl.visibility != "restricted":
            raise ValueError("Restricted classification cannot have broad visibility.")


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    document: DocumentRecord
    text: str
    content_hash: str

    @property
    def metadata(self):
        acl = self.document.acl
        return {
            "document_id": acl.document_id, "dataset_id": self.document.dataset_id,
            "tenant_id": acl.tenant_id, "visibility": acl.visibility,
            "data_domain": acl.data_domain, "classification": acl.classification,
            "allowed_roles": sorted(acl.allowed_roles), "allowed_groups": sorted(acl.allowed_groups),
            "allowed_users": sorted(acl.allowed_users), "mode": acl.mode,
            "policy_version": acl.policy_version, "acl_hash": acl.acl_hash,
            "source_uri": self.document.source_uri, "content_hash": self.content_hash,
        }


def plain_text_chunks(raw):
    text = raw.decode("utf-8")
    return [text[i:i+1200] for i in range(0, len(text), 1200) if text[i:i+1200].strip()]


class SyntheticDocumentStore:
    """Authoritative metadata/content registry for bounded synthetic exercises."""

    def __init__(self, dataset_domains):
        if (type(dataset_domains) is not dict or not dataset_domains
            or any(type(k) is not str or not _ID.fullmatch(k) or v not in DOMAINS
                   for k, v in dataset_domains.items())):
            raise ValueError("Trusted dataset-domain allowlist required.")
        self.dataset_domains = MappingProxyType(dict(dataset_domains))
        self._documents = {}
        self._chunks = {}
        self._revision = 0
        self._lock = threading.RLock()

    def _validate(self, document):
        if (type(document) is not DocumentRecord or document.revoked
            or self.dataset_domains.get(document.dataset_id) != document.acl.data_domain):
            raise AuthorizationDenied("Source metadata denied.")

    def snapshot(self):
        with self._lock:
            return self._revision, dict(self._documents), dict(self._chunks)

    def ingest(self, document, raw, *, parser=plain_text_chunks):
        # Authorization metadata is validated before decoding/parsing content.
        self._validate(document)
        if type(raw) is not bytes or not 1 <= len(raw) <= 1_000_000:
            raise ValueError("Bounded synthetic document required.")
        with self._lock:
            revision = self._revision
            prior = self._documents.get(document.acl.document_id)
            if prior is not None and prior != document:
                raise AuthorizationDenied("Policy update required before re-ingestion.")
        try:
            texts = parser(raw)
            if (type(texts) is not list or not 1 <= len(texts) <= 128
                or any(type(t) is not str or not t.strip() or len(t) > 1200 for t in texts)):
                raise ValueError("Invalid parsed chunks.")
            chunks = [
                ChunkRecord(
                    f"{document.acl.document_id}-{document.acl.policy_version}-{index}",
                    document, text, hashlib.sha256(text.encode("utf-8")).hexdigest(),
                )
                for index, text in enumerate(texts)
            ]
            with self._lock:
                if self._revision != revision:
                    raise AuthorizationDenied("Ingestion policy snapshot changed.")
                # Replace both maps only after every chunk has been validated.
                docs = dict(self._documents)
                staged = {k:v for k,v in self._chunks.items()
                          if v.document.acl.document_id != document.acl.document_id}
                docs[document.acl.document_id] = document
                staged.update({c.chunk_id: c for c in chunks})
                self._documents, self._chunks = docs, staged
                self._revision += 1
        except Exception:
            logging.getLogger(__name__).info("ingestion decision=reject")
            raise
        logging.getLogger(__name__).info("ingestion decision=allow")
        return tuple(chunks)

    def update_policy(self, acl):
        if type(acl) is not DocumentACL:
            raise ValueError("Validated policy required.")
        with self._lock:
            old = self._documents.get(acl.document_id)
            if old is None or old.revoked or acl.policy_version != old.acl.policy_version + 1:
                raise AuthorizationDenied("Monotonic active policy update required.")
            new = replace(old, acl=acl)
            self._validate(new)
            if acl.tenant_id != old.acl.tenant_id:
                raise AuthorizationDenied("Tenant reassignment denied.")
            self._documents[acl.document_id] = new
            self._chunks = {k:v for k,v in self._chunks.items()
                            if v.document.acl.document_id != acl.document_id}
            self._revision += 1
            return new

    def revoke(self, document_id):
        with self._lock:
            old = self._documents.get(document_id)
            if old is None:
                raise AuthorizationDenied("Unknown policy.")
            self._documents[document_id] = replace(old, revoked=True)
            self._chunks = {k:v for k,v in self._chunks.items()
                            if v.document.acl.document_id != document_id}
            self._revision += 1
