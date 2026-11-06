"""Pure authorization contracts for synthetic Entra/MCP/RAG testing.

The existing EntraTokenVerifier must validate the actual JWT FIRST.
Never build SecurityContext from model arguments, browser JSON, or a
decoded-but-unverified JWT. This module does not issue or verify tokens.
The ACL functions are not wired to RAGFlow or production data sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import time
from collections.abc import Mapping

from mcp.server.auth.provider import AccessToken


class AuthorizationDenied(PermissionError):
    """A resource is not accessible to this verified principal."""


def _values(value, label: str) -> frozenset[str]:
    if not isinstance(value, (tuple, list, set, frozenset)):
        raise ValueError(f"Invalid {label}.")
    if any(type(item) is not str or not item.strip() for item in value):
        raise ValueError(f"Invalid {label}.")
    return frozenset(value)


def _identity(value: str, label: str) -> str:
    if type(value) is not str or not value.strip() or value != value.strip():
        raise ValueError(f"Invalid {label}.")
    return value


@dataclass(frozen=True)
class SecurityContext:
    tenant_id: str
    user_oid: str
    roles: frozenset[str] = field(default_factory=frozenset)
    groups: frozenset[str] = field(default_factory=frozenset)
    scopes: frozenset[str] = field(default_factory=frozenset)
    groups_complete: bool = True

    def __post_init__(self):
        _identity(self.tenant_id, "tenant")
        _identity(self.user_oid, "user")
        for name in ("roles", "groups", "scopes"):
            value = getattr(self, name)
            if type(value) is not frozenset:
                raise ValueError(f"Invalid {name}.")
            _values(value, name)
        if type(self.groups_complete) is not bool:
            raise ValueError("Invalid group completeness.")


def from_verified_access_token(
    verified_token: AccessToken,
    *,
    expected_tenant: str,
    expected_issuer: str,
    expected_audience: str,
) -> SecurityContext:
    """Normalize a token ALREADY authenticated by the configured verifier.

    This is a defense-in-depth consistency check, not JWT validation.
    Group-overage is NOT resolved here: group-gated access fails closed
    until trusted server code resolves current membership via Graph.
    """
    if not isinstance(verified_token, AccessToken):
        raise AuthorizationDenied("Verified token required.")
    claims = verified_token.claims
    if not isinstance(claims, dict):
        raise AuthorizationDenied("Verified token claims missing.")
    if (
        claims.get("tid") != expected_tenant
        or claims.get("iss") != expected_issuer
        or claims.get("aud") != expected_audience
        or verified_token.resource != expected_audience
        or not isinstance(claims.get("oid"), str)
        or not claims["oid"].strip()
        or type(verified_token.expires_at) not in (float, int)
        or verified_token.expires_at <= time.time()
    ):
        raise AuthorizationDenied("Invalid verified identity context.")

    role_claim = claims.get("roles", [])
    group_claim = claims.get("groups", [])
    scope_claim = claims.get("scp", "")
    if (
        type(role_claim) is not list
        or type(group_claim) is not list
        or type(scope_claim) is not str
        or type(verified_token.scopes) is not list
    ):
        raise AuthorizationDenied("Invalid authorization claims.")

    overage = (
        claims.get("hasgroups") is True
        or (
            isinstance(claims.get("_claim_names"), dict)
            and "groups" in claims["_claim_names"]
        )
    )
    if overage and group_claim:
        raise AuthorizationDenied("Conflicting group claims.")
    try:
        roles = _values(role_claim, "roles")
        groups = _values(group_claim, "groups")
        scopes = _values(scope_claim.split(), "scopes")
        verified_scopes = _values(verified_token.scopes, "scopes")
        if scopes != verified_scopes:
            raise ValueError("Scope mismatch.")
        return SecurityContext(
            tenant_id=claims["tid"],
            user_oid=claims["oid"],
            roles=roles,
            groups=groups,
            scopes=scopes,
            groups_complete=not overage,
        )
    except ValueError:
        raise AuthorizationDenied("Invalid authorization claims.") from None


@dataclass(frozen=True)
class ToolPolicy:
    roles: frozenset[str] = field(default_factory=frozenset)
    groups: frozenset[str] = field(default_factory=frozenset)
    scopes: frozenset[str] = field(default_factory=frozenset)
    mode: str = "any"

    def __post_init__(self):
        if self.mode not in ("any", "all"):
            raise ValueError("Invalid tool policy mode.")
        for name in ("roles", "groups", "scopes"):
            value = getattr(self, name)
            if type(value) is not frozenset:
                raise ValueError("Invalid tool policy.")
            _values(value, name)
        if not (self.roles or self.groups or self.scopes):
            raise ValueError("Tool policy must be restrictive.")


def authorize_tool(
    tool_name: str,
    user: SecurityContext,
    policies: Mapping[str, ToolPolicy],
) -> None:
    """Authorize from trusted server-defined policies, never model inputs.

    In particular, an absent group criterion is NOT an automatic True
    in an OR; this corrects an unsafe illustrative handout expression.
    """
    if type(user) is not SecurityContext or type(tool_name) is not str:
        raise AuthorizationDenied("Trusted security context required.")
    policy = policies.get(tool_name) if isinstance(policies, Mapping) else None
    if type(policy) is not ToolPolicy:
        raise AuthorizationDenied("Tool is not authorized.")
    if not policy.scopes.issubset(user.scopes):
        raise AuthorizationDenied("Required scope missing.")
    if policy.groups and not user.groups_complete:
        raise AuthorizationDenied("Group membership is unresolved.")

    role_match = bool(policy.roles & user.roles) if policy.roles else None
    group_match = bool(policy.groups & user.groups) if policy.groups else None
    checks = [value for value in (role_match, group_match) if value is not None]

    if checks:
        permitted = all(checks) if policy.mode == "all" else any(checks)
        if not permitted:
            raise AuthorizationDenied("Tool is not authorized.")


@dataclass(frozen=True)
class DocumentACL:
    """Authoritative source ACL; copy its digest/version to every chunk."""

    document_id: str
    tenant_id: str
    visibility: str
    data_domain: str
    classification: str
    allowed_roles: frozenset[str] = field(default_factory=frozenset)
    allowed_groups: frozenset[str] = field(default_factory=frozenset)
    allowed_users: frozenset[str] = field(default_factory=frozenset)
    mode: str = "any"
    policy_version: int = 1

    def __post_init__(self):
        for key in ("document_id", "tenant_id", "data_domain", "classification"):
            _identity(getattr(self, key), key)
        if self.visibility not in ("public", "authenticated", "restricted"):
            raise ValueError("Invalid ACL visibility.")
        if self.mode not in ("any", "all"):
            raise ValueError("Invalid ACL mode.")
        if type(self.policy_version) is not int or self.policy_version < 1:
            raise ValueError("Invalid ACL version.")
        for key in ("allowed_roles", "allowed_groups", "allowed_users"):
            value = getattr(self, key)
            if type(value) is not frozenset:
                raise ValueError("Invalid ACL entries.")
            _values(value, key)
        if self.visibility == "restricted" and not (
            self.allowed_roles or self.allowed_groups or self.allowed_users
        ):
            raise ValueError("Restricted documents need an explicit ACL.")

    @property
    def acl_hash(self) -> str:
        content = {
            "document_id": self.document_id,
            "tenant_id": self.tenant_id,
            "visibility": self.visibility,
            "data_domain": self.data_domain,
            "classification": self.classification,
            "roles": sorted(self.allowed_roles),
            "groups": sorted(self.allowed_groups),
            "users": sorted(self.allowed_users),
            "mode": self.mode,
            "version": self.policy_version,
        }
        canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def document_is_authorized(document: DocumentACL, user: SecurityContext) -> bool:
    if type(document) is not DocumentACL or type(user) is not SecurityContext:
        return False
    if document.tenant_id != user.tenant_id:
        return False
    if document.visibility in ("public", "authenticated"):
        return True
    if document.allowed_groups and not user.groups_complete:
        return False

    matches = [
        bool(document.allowed_roles & user.roles)
        if document.allowed_roles else None,
        bool(document.allowed_groups & user.groups)
        if document.allowed_groups else None,
        user.user_oid in document.allowed_users if document.allowed_users else None,
    ]
    checks = [match for match in matches if match is not None]
    return bool(checks) and (
        all(checks) if document.mode == "all" else any(checks)
    )


def authorized_document_ids(
    documents: Mapping[str, DocumentACL],
    user: SecurityContext,
) -> frozenset[str]:
    """Candidate prefilter contract; apply BEFORE ranking/search."""
    if not isinstance(documents, Mapping):
        raise ValueError("Authoritative ACL mapping required.")
    if any(
        type(document) is not DocumentACL or identifier != document.document_id
        for identifier, document in documents.items()
    ):
        raise ValueError("Invalid authoritative ACL mapping.")
    return frozenset(
        identifier for identifier, document in documents.items()
        if document_is_authorized(document, user)
    )


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    tenant_id: str
    policy_version: int
    acl_hash: str

    def __post_init__(self):
        for key in ("chunk_id", "document_id", "tenant_id"):
            _identity(getattr(self, key), key)
        if type(self.policy_version) is not int or self.policy_version < 1:
            raise ValueError("Invalid chunk policy version.")
        if (
            type(self.acl_hash) is not str
            or len(self.acl_hash) != 64
            or any(ch not in "0123456789abcdef" for ch in self.acl_hash)
        ):
            raise ValueError("Invalid chunk ACL digest.")


def verify_retrieved_chunks(
    chunks: list[RetrievedChunk],
    documents: Mapping[str, DocumentACL],
    user: SecurityContext,
) -> list[RetrievedChunk]:
    """Post-retrieval deny-by-default verification BEFORE LLM context."""
    if type(chunks) is not list or type(user) is not SecurityContext:
        raise ValueError("Trusted retrieval inputs required.")
    eligible = authorized_document_ids(documents, user)
    verified = []
    for chunk in chunks:
        if type(chunk) is not RetrievedChunk:
            raise ValueError("Invalid retrieved chunk.")
        doc = documents.get(chunk.document_id)
        if (
            chunk.document_id in eligible
            and doc is not None
            and chunk.tenant_id == doc.tenant_id
            and chunk.policy_version == doc.policy_version
            and chunk.acl_hash == doc.acl_hash
        ):
            verified.append(chunk)
    return verified
