"""Offline, signed-JWT OAuth callback tests.

The fake exchanger exists only inside test application instances.
No Microsoft authorization endpoint is contacted.
"""

import asyncio
import base64
import hashlib
import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest

from cryptography.hazmat.primitives.asymmetric import rsa

from src.gateway.app import create_app
from src.gateway.oauth_flow import (
    OAUTH_STATE_COOKIE,
    StudentOAuthConfig,
    StudentOAuthFlowStore,
)
from src.gateway.oauth_routes import (
    install_browser_oauth_routes,
)
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    StudentWebSessionStore,
)
from src.mcp_server.entra_token_verifier import (
    EntraTokenVerifier,
)


TENANT = "11111111-1111-4111-8111-111111111111"
API = "22222222-2222-4222-8222-222222222222"
WEB = "33333333-3333-4333-8333-333333333333"
OID_A = "44444444-4444-4444-8444-444444444444"
OID_B = "55555555-5555-4555-8555-555555555555"

ORIGIN = "https://chat.example.test"
ISSUER = f"https://login.microsoftonline.com/{TENANT}/v2.0"
LOOKUP = {(TENANT, OID_A): "S10001"}


@pytest.fixture
def env(monkeypatch):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    verifier = EntraTokenVerifier(
        tenant_id=TENANT,
        audience=API,
    )
    monkeypatch.setattr(
        verifier._jwks_client,
        "get_signing_key_from_jwt",
        lambda raw: SimpleNamespace(
            key=key.public_key()
        ),
    )

    def sign(oid=OID_A, *, audience=API):
        now = int(time.time())

        return jwt.encode(
            {
                "iss": ISSUER,
                "aud": audience,
                "tid": TENANT,
                "oid": oid,
                "azp": WEB,
                "scp": "academic.read",
                "ver": "2.0",
                "iat": now,
                "nbf": now,
                "exp": now + 600,
            },
            key,
            algorithm="RS256",
            headers={"kid": "local-research-only-key"},
        )

    store = StudentWebSessionStore(
        student_lookup=LOOKUP,
        allowed_issuer=ISSUER,
    )

    config = StudentOAuthConfig(
        tenant_id=TENANT,
        web_client_id=WEB,
        api_app_id=API,
        redirect_uri=ORIGIN + "/auth/callback",
    )

    flow = StudentOAuthFlowStore(config=config)
    exchanges = []

    async def fake_exchange(
        *, code, code_verifier, redirect_uri
    ):
        exchanges.append(
            (code, code_verifier, redirect_uri)
        )

        if redirect_uri != config.redirect_uri:
            raise PermissionError

        if code == "research-code-a":
            return sign()

        if code == "research-code-b":
            return sign(OID_B)

        if code == "invalid-signature":
            foreign = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            claims = jwt.decode(
                sign(),
                options={"verify_signature": False},
            )

            return jwt.encode(
                claims,
                foreign,
                algorithm="RS256",
            )

        raise PermissionError

    async def runner(**kwargs):
        return SimpleNamespace(
            answer="Synthetic proposal only.",
            plan_cards=None,
            stopped_reason="answered",
            grounded=True,
        )

    app = create_app(
        token_verifier=verifier,
        student_lookup=LOOKUP,
        issuer=ISSUER,
        term_id="2027SP",
    )

    install_browser_session_routes(
        app,
        session_store=store,
        token_verifier=verifier,
        student_lookup=LOOKUP,
        allowed_issuer=ISSUER,
        session_origin=ORIGIN,
        term_id="2027SP",
        assistant_runner=runner,
    )

    install_browser_oauth_routes(
        app,
        flow_store=flow,
        exchange_code=fake_exchange,
    )

    return SimpleNamespace(
        app=app,
        store=store,
        flow=flow,
        config=config,
        exchanges=exchanges,
        fake_exchange=fake_exchange,
        verifier=verifier,
    )


async def begin(client):
    response = await client.get("/auth/login")

    assert response.status_code == 303
    assert OAUTH_STATE_COOKIE in client.cookies

    parsed = urlsplit(response.headers["location"])
    assert parsed.hostname == "login.microsoftonline.com"

    parameters = parse_qs(parsed.query)
    assert parameters["code_challenge_method"] == ["S256"]

    return parameters


def test_login_issues_verified_server_side_session(env):
    async def check():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=env.app),
            base_url=ORIGIN,
        ) as client:
            values = await begin(client)

            callback = await client.get(
                "/auth/callback",
                params={
                    "state": values["state"][0],
                    "code": "research-code-a",
                },
            )

            assert callback.status_code == 303
            assert callback.headers["location"] == "/leo/session"
            assert SESSION_COOKIE_NAME in client.cookies
            assert OAUTH_STATE_COOKIE not in client.cookies
            assert env.store.count() == 1

            assert len(env.exchanges) == 1
            code, secret, redirect = env.exchanges[0]

            assert code == "research-code-a"
            assert redirect == env.config.redirect_uri

            expected_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(
                    secret.encode("ascii")
                ).digest()
            ).rstrip(b"=").decode("ascii")

            assert expected_challenge == (
                values["code_challenge"][0]
            )

            cookie_header = next(
                item
                for item in callback.headers.get_list(
                    "set-cookie"
                )
                if item.startswith(
                    SESSION_COOKIE_NAME + "="
                )
            )

            assert "Secure" in cookie_header
            assert "HttpOnly" in cookie_header
            assert "SameSite=strict" in cookie_header
            assert "Path=/" in cookie_header

            status = await client.get(
                "/api/student/session"
            )

            assert status.status_code == 200
            assert status.json()["student_id"] == "S10001"
            assert len(status.json()["csrf_token"]) >= 30

            assert (
                await client.get("/leo/session")
            ).status_code == 200

            assert "research-code-a" not in callback.text
            assert secret not in callback.text

            csrf = status.json()["csrf_token"]

            logout = await client.post(
                "/auth/logout",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf,
                },
            )
            assert logout.status_code == 200
            assert env.store.count() == 0

    asyncio.run(check())


def test_callback_state_replay_is_rejected(env):
    async def check():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=env.app),
            base_url=ORIGIN,
        ) as client:
            state = (await begin(client))["state"][0]

            first = await client.get(
                "/auth/callback",
                params={
                    "state": state,
                    "code": "research-code-a",
                },
            )
            assert first.status_code == 303

            second = await client.get(
                "/auth/callback",
                params={
                    "state": state,
                    "code": "research-code-a",
                },
            )

            assert second.status_code == 401
            assert len(env.exchanges) == 1
            assert env.store.count() == 1

    asyncio.run(check())


def test_missing_cookie_denied_but_owner_can_complete(env):
    async def check():
        async with (
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=env.app),
                base_url=ORIGIN,
            ) as a,
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=env.app),
                base_url=ORIGIN,
            ) as b,
        ):
            state = (await begin(a))["state"][0]

            denied = await b.get(
                "/auth/callback",
                params={
                    "state": state,
                    "code": "research-code-a",
                },
            )
            assert denied.status_code == 401
            assert env.exchanges == []
            assert env.store.count() == 0

            replay = await a.get(
                "/auth/callback",
                params={
                    "state": state,
                    "code": "research-code-a",
                },
            )
            # Browser B had no valid correlation cookie.
            # Its request did not consume A's pending state.
            # Browser A can still finish the legitimate flow.
            assert replay.status_code == 303
            assert len(env.exchanges) == 1
            assert env.store.count() == 1

    asyncio.run(check())


def test_wrong_well_formed_cookie_consumes_state(env):
    """A mismatched but valid-length cookie consumes matching state."""

    async def check():
        async with (
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=env.app),
                base_url=ORIGIN,
            ) as a,
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=env.app),
                base_url=ORIGIN,
            ) as b,
        ):
            state = (await begin(a))["state"][0]

            # Valid cookie shape, but not the original
            # browser's private correlation secret.
            b.cookies.set(
                OAUTH_STATE_COOKIE,
                "x" * 43,
                domain="chat.example.test",
                path="/",
            )

            denied = await b.get(
                "/auth/callback",
                params={
                    "state": state,
                    "code": "research-code-a",
                },
            )

            assert denied.status_code == 401
            assert env.exchanges == []
            assert env.store.count() == 0

            # A matched state is consumed once the store
            # receives a well-formed, mismatched cookie.
            replay = await a.get(
                "/auth/callback",
                params={
                    "state": state,
                    "code": "research-code-a",
                },
            )

            assert replay.status_code == 401
            assert env.exchanges == []
            assert env.store.count() == 0

    asyncio.run(check())


@pytest.mark.parametrize(
    "code",
    [
        "research-code-b",
        "invalid-signature",
        "unknown-code",
    ],
)
def test_unauthorized_or_invalid_token_never_issues_session(
    env, code
):
    async def check():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=env.app),
            base_url=ORIGIN,
        ) as client:
            state = (await begin(client))["state"][0]

            response = await client.get(
                "/auth/callback",
                params={"state": state, "code": code},
            )

            assert response.status_code == 401
            assert SESSION_COOKIE_NAME not in client.cookies
            assert env.store.count() == 0

    asyncio.run(check())


def test_https_and_host_are_required(env):
    async def check():
        for url in (
            "http://chat.example.test",
            "https://evil.example.test",
        ):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=env.app),
                base_url=url,
            ) as client:
                response = await client.get("/auth/login")
                assert response.status_code == 403

        assert env.exchanges == []
        assert env.store.count() == 0

    asyncio.run(check())


def test_invalid_callback_parameters_fail_closed(env):
    async def check():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=env.app),
            base_url=ORIGIN,
        ) as client:
            values = await begin(client)
            state = values["state"][0]

            denied = await client.get(
                "/auth/callback",
                params=[
                    ("state", state),
                    ("state", state),
                    ("code", "research-code-a"),
                ],
            )

            assert denied.status_code == 401
            assert env.exchanges == []
            assert env.store.count() == 0

    asyncio.run(check())


def test_oauth_installation_requires_existing_session_routes():
    app = create_app(
        token_verifier=None,
        student_lookup={},
        issuer="https://example.invalid/",
        term_id="2027SP",
    )

    config = StudentOAuthConfig(
        tenant_id=TENANT,
        web_client_id=WEB,
        api_app_id=API,
        redirect_uri=ORIGIN + "/auth/callback",
    )

    with pytest.raises(ValueError):
        install_browser_oauth_routes(
            app,
            flow_store=StudentOAuthFlowStore(
                config=config
            ),
            exchange_code=lambda **kwargs: None,
        )

    routes = {route.path for route in app.routes}

    assert "/auth/login" not in routes
    assert "/auth/callback" not in routes


def test_default_gateway_remains_fail_closed():
    from src.gateway.app import app

    routes = {route.path for route in app.routes}
    assert "/auth/login" not in routes
    assert "/auth/callback" not in routes
    assert "/api/student/session" not in routes
