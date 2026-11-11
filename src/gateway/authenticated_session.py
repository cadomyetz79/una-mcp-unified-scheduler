"""Development-only authenticated session bound to an MCP student identity.

Only call from a trusted application boundary *after* Entra JWT verification.
The protected MCP server must independently authenticate the same delegated
token and authorize every student-scoped tool; this is defense in depth,
not a replacement for the server's policy. No user prompt is used here.
"""

from dataclasses import dataclass, field
import time
from collections.abc import Mapping

from mcp.server.auth.provider import AccessToken

from src.mcp_server.student_access import (
    resolve_authenticated_student_id,
)


PROTECTED_DEMO_MCP_URL = "http://127.0.0.1:8002/mcp"


@dataclass(frozen=True)
class AuthenticatedStudentSession:
    """Resolved academic identity and the SAME delegated bearer credential.

    Only for a local synthetic test client; do not serialize or expose to an
    LLM, chat history, n8n intermediateSteps, or research evidence.
    """
    student_id: str
    bearer_token: str = field(repr=False)
    mcp_url: str = PROTECTED_DEMO_MCP_URL


def session_from_verified_token(
    *,
    access_token: AccessToken | None,
    student_lookup: Mapping[tuple[str, str], str],
    allowed_issuer: str,
) -> AuthenticatedStudentSession:
    """Derive the demo student's ID from a verified identity, not a prompt.

    The trusted caller must obtain access_token from verified authentication
    middleware. The protected MCP service re-verifies this same token.
    """
    student_id = resolve_authenticated_student_id(
        access_token=access_token,
        student_lookup=student_lookup,
        allowed_issuer=allowed_issuer,
    )
    token = access_token.token

    if (
        not isinstance(token, str)
        or not token
        or token != token.strip()
        or any(character.isspace() for character in token)
    ):
        raise PermissionError("Invalid delegated MCP access token.")

    expires_at = access_token.expires_at
    if expires_at is not None and expires_at <= time.time():
        raise PermissionError("Expired delegated MCP access token.")

    return AuthenticatedStudentSession(
        student_id=student_id,
        bearer_token=token,
    )
