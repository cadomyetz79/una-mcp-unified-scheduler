"""Opt-in HTTPS browser session routes for the unified Leo gateway.

No login, OAuth callback, token issuance, or development authentication
bypass exists here. Sessions must be issued by a separate trusted,
verified identity-provider callback.

Only isolated synthetic tests install these routes in this phase.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from src.gateway.app import ChatRequest, ChatResponse
from src.gateway.plan_context import (
    continuation_cards_safe,
    from_verified_planner_result,
    resolve_add_day_followup,
    resolve_start_time_followup,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    StudentWebSessionStore,
    StalePlanContextError,
)
from src.mcp_server.student_access import (
    resolve_authenticated_student_id,
)


def install_browser_session_routes(
    app: FastAPI,
    *,
    session_store: StudentWebSessionStore,
    token_verifier: Any,
    student_lookup: Mapping[tuple[str, str], str],
    allowed_issuer: str,
    session_origin: str,
    term_id: str,
    assistant_runner: Any,
) -> None:
    """Install browser-session routes only with trusted configuration."""

    parsed = urlsplit(session_origin or "")

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or session_origin != f"https://{parsed.netloc}"
    ):
        raise ValueError("Exact HTTPS session origin required.")

    if (
        not isinstance(session_store, StudentWebSessionStore)
        or not callable(getattr(token_verifier, "verify_token", None))
        or not isinstance(student_lookup, Mapping)
        or not isinstance(allowed_issuer, str)
        or not allowed_issuer
        or not isinstance(term_id, str)
        or not term_id
        or not callable(assistant_runner)
    ):
        raise ValueError("Trusted session configuration required.")

    if getattr(app.state, "browser_session_routes_installed", False):
        raise ValueError("Session routes already installed.")

    host = parsed.netloc

    def check_request_origin(
        request: Request,
        *,
        require_origin: bool,
    ) -> None:
        if (
            request.url.scheme != "https"
            or request.headers.get("host") != host
            or request.headers.get("sec-fetch-site")
            not in (None, "same-origin")
        ):
            raise HTTPException(403, "Origin verification failed.")

        request_origin = request.headers.get("origin")

        if require_origin:
            if request_origin != session_origin:
                raise HTTPException(403, "Origin verification failed.")
        elif request_origin is not None:
            if request_origin != session_origin:
                raise HTTPException(403, "Origin verification failed.")

        # Never accept competing browser-cookie and bearer credentials.
        if request.headers.get("authorization"):
            raise HTTPException(400, "Use browser session only.")

    async def authenticate_session(request: Request, *, csrf=False):
        cookie = request.cookies.get(SESSION_COOKIE_NAME)

        try:
            session = session_store.resolve(
                cookie_value=cookie,
                csrf_token=(
                    request.headers.get("x-csrf-token")
                    if csrf else None
                ),
                require_csrf=csrf,
            )
        except PermissionError:
            raise HTTPException(
                403 if csrf and cookie else 401,
                "Session or CSRF verification failed.",
            ) from None

        # A valid stored session is not sufficient by itself.
        # Reverify the original delegated token on every request.
        try:
            verified = await token_verifier.verify_token(
                session.bearer_token
            )
        except Exception:
            verified = None

        if verified is None:
            raise HTTPException(
                401, "Session authentication required."
            )

        try:
            current_student = resolve_authenticated_student_id(
                access_token=verified,
                student_lookup=student_lookup,
                allowed_issuer=allowed_issuer,
            )
        except PermissionError:
            raise HTTPException(
                403, "Student access denied."
            ) from None

        if (
            current_student != session.student_id
            or verified.token != session.bearer_token
        ):
            raise HTTPException(
                403, "Student access denied."
            )

        return session

    @app.get("/api/student/session")
    async def session_status(request: Request):
        check_request_origin(request, require_origin=False)
        session = await authenticate_session(request)

        try:
            csrf_token = session_store.rotate_csrf(
                cookie_value=request.cookies.get(
                    SESSION_COOKIE_NAME
                )
            )
        except PermissionError:
            raise HTTPException(
                401, "Session authentication required."
            ) from None

        return {
            "authenticated": True,
            "student_id": session.student_id,
            "csrf_token": csrf_token,
            "synthetic_data": True,
        }

    @app.post(
        "/api/student/session/chat",
        response_model=ChatResponse,
    )
    async def session_chat(
        payload: ChatRequest,
        request: Request,
    ):
        check_request_origin(request, require_origin=True)
        session = await authenticate_session(
            request, csrf=True
        )

        # Authentication, origin, and CSRF have
        # already been verified above. Context is
        # selected only by the server-side cookie.
        cookie = request.cookies.get(
            SESSION_COOKIE_NAME
        )

        try:
            revision, prior_context = session_store.read_plan_snapshot(
                cookie_value=cookie,
                term_id=term_id,
            )
        except PermissionError:
            raise HTTPException(
                401, "Session authentication required."
            ) from None

        # Only a recognized follow-up is reconstructed.
        # All other requests retain their original wording.
        # This does not bypass the agent's privacy checks.
        resolved = resolve_start_time_followup(
            payload.question,
            prior_context,
            expected_term_id=term_id,
        )

        if resolved is None:
            resolved = resolve_add_day_followup(
                payload.question,
                prior_context,
                expected_term_id=term_id,
            )

        effective_question = (
            resolved if resolved is not None
            else payload.question
        )

        try:
            result = await assistant_runner(
                question=effective_question,
                student_id=session.student_id,
                term_id=term_id,
                bearer_token=session.bearer_token,
            )
        except Exception:
            raise HTTPException(
                503, "Scheduling service is unavailable."
            ) from None

        cards = getattr(result, "plan_cards", None)

        if not (
            getattr(result, "stopped_reason", None)
            == "answered"
            and getattr(result, "grounded", False) is True
            and type(cards) is dict
            and cards.get("schema_version") == "leo-team-plan-v1"
            and cards.get("status") == "proposed_only"
            and cards.get("student_id") == session.student_id
            and cards.get("term_id") == term_id
            and type(cards.get("options")) is list
        ):
            cards = None

        # A valid isolated model plan is not necessarily
        # a valid continuation of earlier requirements.
        continuity_notice = None
        context_to_save = None

        if cards is not None:
            context = from_verified_planner_result(
                result,
                expected_student_id=session.student_id,
                expected_term_id=term_id,
            )

            if not continuation_cards_safe(
                original_question=payload.question,
                prior_context=prior_context,
                resolved_question=resolved,
                candidate_context=context,
            ):
                cards = None
                continuity_notice = (
                    "I couldn't verify a revised schedule "
                    "that safely preserves your previous "
                    "requirements. To replace the previous plan, "
                    "say, for example: Start a new schedule: "
                    "Plan CIS376 and CIS410. Then add supported "
                    "restrictions in follow-up messages. "
                    "No schedule was saved or enrollment performed."
                )

            elif context is not None:
                context_to_save = context

        # Recheck even cardless replies: revoked sessions and stale model
        # prose must not escape merely because no proposal can be saved.
        try:
            session_store.commit_plan_context(
                cookie_value=cookie,
                expected_revision=revision,
                context=context_to_save,
            )
        except PermissionError:
            raise HTTPException(
                401, "Session authentication required."
            ) from None
        except StalePlanContextError:
            raise HTTPException(
                409,
                "Your schedule changed while this request was running. "
                "Please send your request again using the latest plan. "
                "This result was not saved; no enrollment was performed.",
            ) from None

        return ChatResponse(
            answer=(
                continuity_notice
                if continuity_notice is not None
                else result.answer
            ),
            plan_cards=cards,
        )

    @app.post("/auth/logout")
    async def logout(request: Request):
        check_request_origin(request, require_origin=True)
        await authenticate_session(request, csrf=True)

        session_store.revoke(
            cookie_value=request.cookies.get(
                SESSION_COOKIE_NAME
            )
        )

        response = JSONResponse({"signed_out": True})
        response.delete_cookie(
            SESSION_COOKIE_NAME,
            path="/",
            secure=True,
            httponly=True,
            samesite="strict",
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/leo/session", include_in_schema=False)
    async def leo_session_interface():
        # Static HTML only. Session bootstrap and chat
        # still require verified credentials and CSRF.
        return FileResponse(
            Path(__file__).resolve().parent
            / "leo_ui" / "session.html",
            media_type="text/html",
            headers={
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": (
                    "default-src 'none'; "
                    "script-src 'self'; "
                    "style-src 'self'; "
                    "img-src 'self'; "
                    "connect-src 'self'; "
                    "object-src 'none'; "
                    "base-uri 'none'; "
                    "form-action 'none'; "
                    "frame-ancestors 'none'"
                ),
            },
        )

    # Internal-only dependencies for an explicitly installed
    # OAuth callback. Both route sets must use the SAME store,
    # verifier, identity mapping and HTTPS origin.
    app.state.browser_oauth_context = (
        session_origin,
        session_store,
        token_verifier,
        student_lookup,
        allowed_issuer,
    )
    app.state.browser_session_routes_installed = True
