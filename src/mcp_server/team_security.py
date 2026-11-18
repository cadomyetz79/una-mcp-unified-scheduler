"""Authentication and student authorization for team MCP.

Requires verified MCP request context. No development
authentication bypass is enabled.
"""

import os
import logging
from types import MappingProxyType

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier

from src.mcp_server.entra_token_verifier import EntraTokenVerifier
from src.mcp_server.student_access import require_student_read_access, resolve_authenticated_student_id
from src.mcp_server.entra_rbac_acl import from_verified_access_token, authorize_tool, ToolPolicy


RESOURCE_URL = "http://127.0.0.1:8002/mcp"
DEV_ISSUER_URL = "https://example.invalid/"


class RejectAllTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        return None


def select_auth_config(
    *,
    tenant_id: str | None,
    audience: str | None,
) -> tuple[TokenVerifier, str, bool]:
    if bool(tenant_id) != bool(audience):
        raise ValueError(
            "Both UNA_ENTRA_TENANT_ID and "
            "UNA_ENTRA_API_CLIENT_ID are required."
        )

    if not tenant_id:
        return RejectAllTokenVerifier(), DEV_ISSUER_URL, True

    verifier = EntraTokenVerifier(
        tenant_id=tenant_id,
        audience=audience,
    )
    return verifier, verifier.issuer, False


TOKEN_VERIFIER, ISSUER_URL, VALIDATE_TOKEN_RESOURCE = (
    select_auth_config(
        tenant_id=os.getenv("UNA_ENTRA_TENANT_ID"),
        audience=os.getenv("UNA_ENTRA_API_CLIENT_ID"),
    )
)

# No production identity mappings are configured.
STUDENT_LOOKUP: dict[tuple[str, str], str] = {}


def authorize_student_request(student_id: str) -> str:
    return require_student_read_access(
        access_token=get_access_token(),
        student_id=student_id,
        student_lookup=STUDENT_LOOKUP,
        allowed_issuer=ISSUER_URL,
    )


def authorize_catalog_request() -> None:
    token = get_access_token()

    if token is None:
        raise PermissionError("Authentication required.")

    claims = token.claims
    if (
        not isinstance(claims, dict)
        or claims.get("iss") != ISSUER_URL
    ):
        raise PermissionError("Untrusted token issuer.")

    if "academic.read" not in token.scopes:
        raise PermissionError("Insufficient academic permissions.")

    if not all(
        isinstance(claims.get(name), str)
        and claims[name].strip()
        for name in ("tid", "oid")
    ):
        raise PermissionError("Missing verified user identity.")


# These are trusted deployment configuration, never token/model-selected.
AUTH_TENANT = os.getenv("UNA_ENTRA_TENANT_ID")
AUTH_AUDIENCE = os.getenv("UNA_ENTRA_API_CLIENT_ID")
ACADEMIC_TOOL_POLICIES = MappingProxyType({
    name: ToolPolicy(
        roles=frozenset({"RAG.Student"}), scopes=frozenset({"academic.read"}),
        mode="all",
    )
    for name in (
        "get_student_record", "get_course_history", "get_course",
        "search_courses", "get_course_sections", "get_student_enrollments",
    )
})


def authorize_tool_request(tool_name: str):
    """MCP middleware has verified the token; enforce policy on every call."""
    token = get_access_token()
    try:
        user = from_verified_access_token(
            token, expected_tenant=AUTH_TENANT,
            expected_issuer=ISSUER_URL, expected_audience=AUTH_AUDIENCE,
        )
        authorize_tool(tool_name, user, ACADEMIC_TOOL_POLICIES)
        # All six academic operations are part of the mapped-student service.
        resolve_authenticated_student_id(
            access_token=token, student_lookup=STUDENT_LOOKUP,
            allowed_issuer=ISSUER_URL,
        )
    except Exception:
        logging.getLogger(__name__).info("academic_authorization decision=deny")
        raise PermissionError("Academic access denied.") from None
    logging.getLogger(__name__).info("academic_authorization decision=allow")
    return user
