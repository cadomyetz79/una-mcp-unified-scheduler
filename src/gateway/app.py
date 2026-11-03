"""Fail-closed browser API for the synthetic UNA scheduling prototype.

Authentication is verified server-side. No demo login, anonymous academic
access, enrollment operation, or browser-controlled student identity.

The real assistant runner is deliberately not configured in this phase.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from src.mcp_server import team_security
from src.mcp_server.student_access import resolve_authenticated_student_id


_LEO_DIR = Path(__file__).resolve().parent / "leo_ui"


# Only the files required by the approved Leo views
# are published. Original source/research assets remain
# preserved in Git, not accessible through static URLs.
_LEO_PUBLIC_ASSETS = frozenset({
    "styles.css",
    "interactive.css",
    "leo-theme.css",
    "unified.js",
    "una-lion-mark.png",
})


class LeoPublicAssets(StaticFiles):
    async def get_response(self, path, scope):
        if path not in _LEO_PUBLIC_ASSETS:
            raise HTTPException(
                status_code=404,
                detail="Asset not found.",
            )
        return await super().get_response(path, scope)

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    plan_cards: dict | None = None


def create_app(
    *,
    token_verifier: Any,
    student_lookup: Mapping[tuple[str, str], str],
    issuer: str,
    term_id: str,
    assistant_runner: Any = None,
) -> FastAPI:
    """Construct the gateway with trusted server-side dependencies."""

    api = FastAPI(
        title="UNA Synthetic Scheduling Gateway",
        version="0.1.0",
    )

    # Static UI contains no academic records or sign-in credentials.
    # The browser authentication flow remains unconfigured.
    api.mount(
        "/leo-assets",
        LeoPublicAssets(directory=_LEO_DIR),
        name="leo-assets",
    )

    @api.get("/", include_in_schema=False)
    async def frontend():
        return FileResponse(
            _LEO_DIR / "preview.html",
            media_type="text/html",
            headers={
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": (
                    "default-src 'none'; "
                    "script-src 'self'; "
                    "style-src 'self'; "
                    "connect-src 'self'; "
                    "img-src 'self'; "
                    "object-src 'none'; "
                    "base-uri 'none'; "
                    "form-action 'none'; "
                    "frame-ancestors 'none'"
                ),
            },
        )

    @api.middleware("http")
    async def prevent_academic_response_caching(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @api.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "UNA Synthetic Scheduling Gateway",
            "chat_runner_configured": assistant_runner is not None,
        }

    @api.post("/api/chat", response_model=ChatResponse)
    async def chat(
        payload: ChatRequest,
        authorization: str | None = Header(default=None),
    ):
        # Do not interpret browser-provided identity claims or JWT payloads.
        if not isinstance(authorization, str):
            raise HTTPException(401, "Authentication required.")

        scheme, separator, token = authorization.partition(" ")

        if (
            not separator
            or scheme.lower() != "bearer"
            or not token
            or token != token.strip()
            or any(c.isspace() for c in token)
            or len(token) > 16384
        ):
            raise HTTPException(401, "Invalid authentication.")

        try:
            verified = await token_verifier.verify_token(token)
        except Exception:
            verified = None

        if verified is None:
            raise HTTPException(401, "Invalid authentication.")

        try:
            student_id = resolve_authenticated_student_id(
                access_token=verified,
                student_lookup=student_lookup,
                allowed_issuer=issuer,
            )
        except PermissionError:
            raise HTTPException(
                403, "Academic access denied."
            ) from None

        if not payload.question.strip():
            raise HTTPException(422, "Question cannot be empty.")

        # No default demo bypass. Unconfigured services remain unavailable.
        if assistant_runner is None:
            raise HTTPException(
                503, "Scheduling service is not configured."
            )

        try:
            result = await assistant_runner(
                question=payload.question,
                student_id=student_id,
                term_id=term_id,
                bearer_token=token,
            )
        except Exception:
            # Never expose tokens, internal errors, or backend details.
            raise HTTPException(
                503, "Scheduling service is unavailable."
            ) from None

        # Return only the intended public response fields.
        # Internal traces, MCP calls, and security logs are not serialized.
        cards = result.plan_cards

        if (
            getattr(result, "stopped_reason", None) != "answered"
            or getattr(result, "grounded", False) is not True
            or type(cards) is not dict
            or cards.get("status") != "proposed_only"
            or cards.get("student_id") != student_id
            or cards.get("term_id") != term_id
        ):
            cards = None

        return ChatResponse(
            answer=result.answer,
            plan_cards=cards,
        )

    return api


# Production-facing construction: uses existing MCP auth configuration.
# Without authorized Entra configuration and identity mappings, it fails closed.
# Academic chat is intentionally unavailable until a trusted runner is wired.
app = create_app(
    token_verifier=team_security.TOKEN_VERIFIER,
    student_lookup=team_security.STUDENT_LOOKUP,
    issuer=team_security.ISSUER_URL,
    term_id="2027SP",  # Synthetic research term only.
)
