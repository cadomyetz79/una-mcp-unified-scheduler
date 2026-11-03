"""Opt-in OAuth routing contract for the synthetic Leo prototype.

Only trusted application assembly may install this. The module does not
implement an Entra token exchange, configure MSAL, or enable production
sign-in. Tests supply an isolated fake exchanger and locally signed JWTs.

An approved confidential exchange implementation, HTTPS deployment, and
institutional authorization are required before real Entra login.
"""

from collections.abc import Callable
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.gateway.oauth_flow import (
    OAUTH_STATE_COOKIE,
    OAUTH_STATE_COOKIE_MAX_AGE,
    OAUTH_STATE_COOKIE_SAMESITE,
    StudentOAuthFlowStore,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_PATH,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE,
    StudentWebSessionStore,
)
from src.mcp_server.entra_token_verifier import EntraTokenVerifier
from src.mcp_server.student_access import (
    resolve_authenticated_student_id,
)


def install_browser_oauth_routes(
    app: FastAPI,
    *,
    flow_store: StudentOAuthFlowStore,
    exchange_code: Callable,
) -> None:
    """Explicitly install login and callback against existing session routes."""

    context = getattr(app.state, "browser_oauth_context", None)

    if not (
        isinstance(app, FastAPI)
        and getattr(app.state, "browser_session_routes_installed", False)
        and isinstance(context, tuple)
        and len(context) == 5
        and isinstance(flow_store, StudentOAuthFlowStore)
        and callable(exchange_code)
    ):
        raise ValueError("Trusted browser OAuth configuration required.")

    origin, store, verifier, student_lookup, issuer = context
    config = flow_store.config

    if not (
        isinstance(store, StudentWebSessionStore)
        and isinstance(verifier, EntraTokenVerifier)
        and config.origin == origin
        and config.tenant_id == verifier.tenant_id
        and config.api_app_id == verifier.audience
        and issuer == verifier.issuer
    ):
        raise ValueError("OAuth and academic session settings differ.")

    if getattr(app.state, "browser_oauth_routes_installed", False):
        raise ValueError("OAuth routes already installed.")

    if any(
        getattr(route, "path", None) in (
            "/auth/login", "/auth/callback"
        )
        for route in app.routes
    ):
        raise ValueError("OAuth route conflicts.")

    from urllib.parse import urlsplit

    host = urlsplit(origin).netloc

    def require_https_host(request: Request):
        if (
            request.url.scheme != "https"
            or request.headers.get("host") != host
            or request.headers.get("authorization")
        ):
            raise HTTPException(
                status_code=403,
                detail="Origin verification failed.",
            )

    def clear_flow_cookie(response):
        response.delete_cookie(
            key=OAUTH_STATE_COOKIE,
            path="/",
            secure=True,
            httponly=True,
            samesite=OAUTH_STATE_COOKIE_SAMESITE,
        )
        return response

    def failed_login():
        response = JSONResponse(
            status_code=401,
            content={"detail": "Login was not completed."},
        )
        clear_flow_cookie(response)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/auth/login", include_in_schema=False)
    async def begin_login(request: Request):
        require_https_host(request)

        if request.url.query:
            raise HTTPException(400, "Invalid login request.")

        try:
            started = flow_store.begin()
        except Exception:
            raise HTTPException(
                503, "Login cannot be started."
            ) from None

        response = RedirectResponse(
            url=started.authorization_url,
            status_code=303,
        )
        response.set_cookie(
            key=OAUTH_STATE_COOKIE,
            value=started.state_cookie,
            max_age=OAUTH_STATE_COOKIE_MAX_AGE,
            path="/",
            secure=True,
            httponly=True,
            samesite=OAUTH_STATE_COOKIE_SAMESITE,
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/auth/callback", include_in_schema=False)
    async def finish_login(request: Request):
        require_https_host(request)

        # Reject ambiguous or duplicate callback parameters.
        codes = request.query_params.getlist("code")
        states = request.query_params.getlist("state")
        errors = request.query_params.getlist("error")

        if (
            errors
            or len(codes) != 1
            or len(states) != 1
            or not 1 <= len(codes[0]) <= 2048
        ):
            return failed_login()

        try:
            verifier_secret = flow_store.consume(
                state=states[0],
                browser_cookie=request.cookies.get(
                    OAUTH_STATE_COOKIE
                ),
            )
        except PermissionError:
            return failed_login()

        try:
            # A trusted, confidential authorization-code exchange
            # adapter is REQUIRED. No fallback exists.
            raw_token = await exchange_code(
                code=codes[0],
                code_verifier=verifier_secret,
                redirect_uri=config.redirect_uri,
            )

            if (
                not isinstance(raw_token, str)
                or not 30 <= len(raw_token) <= 16384
            ):
                raise PermissionError

            verified = await verifier.verify_token(raw_token)

            if verified is None:
                raise PermissionError

            # Identity must be authorized independently
            # of the callback's code or browser parameters.
            resolve_authenticated_student_id(
                access_token=verified,
                student_lookup=student_lookup,
                allowed_issuer=issuer,
            )

            ticket = store.issue(
                verified_access_token=verified
            )
        except Exception:
            return failed_login()

        # Retire an older browser session on successful replacement.
        store.revoke(
            cookie_value=request.cookies.get(
                SESSION_COOKIE_NAME
            )
        )

        response = RedirectResponse(
            url="/leo/session",
            status_code=303,
        )
        clear_flow_cookie(response)

        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=ticket.cookie_value,
            max_age=max(
                1, int(ticket.expires_at - time.time())
            ),
            path=SESSION_COOKIE_PATH,
            secure=SESSION_COOKIE_SECURE,
            httponly=SESSION_COOKIE_HTTPONLY,
            samesite=SESSION_COOKIE_SAMESITE,
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    app.state.browser_oauth_routes_installed = True
