"""Offline OAuth state/PKCE tests for the unified gateway.

No real Microsoft endpoint, login, callback or token exchange.
"""

import base64
import hashlib
from urllib.parse import parse_qs, urlsplit

import pytest

from src.gateway import oauth_flow as flow
from src.gateway.oauth_flow import (
    StudentOAuthConfig,
    StudentOAuthFlowStore,
)


TENANT = "11111111-1111-4111-8111-111111111111"
WEB = "33333333-3333-4333-8333-333333333333"
API = "22222222-2222-4222-8222-222222222222"
ORIGIN = "https://chat.example.test"
REDIRECT = ORIGIN + "/auth/callback"


def config(**overrides):
    values = {
        "tenant_id": TENANT,
        "web_client_id": WEB,
        "api_app_id": API,
        "redirect_uri": REDIRECT,
    }
    values.update(overrides)
    return StudentOAuthConfig(**values)


def test_trusted_oauth_configuration():
    c = config()

    assert c.origin == ORIGIN
    assert c.scope == f"api://{API}/academic.read"
    assert c.authorize_endpoint == (
        f"https://login.microsoftonline.com/"
        f"{TENANT}/oauth2/v2.0/authorize"
    )


def test_pkce_s256_challenge_and_single_use():
    store = StudentOAuthFlowStore(config=config())
    started = store.begin()

    parsed = urlsplit(started.authorization_url)
    parameters = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert parsed.hostname == "login.microsoftonline.com"
    assert parameters["client_id"] == [WEB]
    assert parameters["redirect_uri"] == [REDIRECT]
    assert parameters["response_type"] == ["code"]
    assert parameters["code_challenge_method"] == ["S256"]
    assert parameters["scope"] == [
        f"api://{API}/academic.read"
    ]

    assert started.state_cookie not in (
        started.authorization_url
    )
    assert started.state_cookie not in repr(started)

    state = parameters["state"][0]

    verifier = store.consume(
        state=state,
        browser_cookie=started.state_cookie,
    )

    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(
            verifier.encode("ascii")
        ).digest()
    ).rstrip(b"=").decode("ascii")

    assert parameters["code_challenge"] == [challenge]

    with pytest.raises(PermissionError):
        store.consume(
            state=state,
            browser_cookie=started.state_cookie,
        )


def test_wrong_browser_cookie_consumes_matching_state():
    store = StudentOAuthFlowStore(config=config())
    started = store.begin()

    state = parse_qs(
        urlsplit(started.authorization_url).query
    )["state"][0]

    with pytest.raises(PermissionError):
        store.consume(
            state=state,
            browser_cookie="x" * 43,
        )

    with pytest.raises(PermissionError):
        store.consume(
            state=state,
            browser_cookie=started.state_cookie,
        )


def test_expired_state_is_rejected(monkeypatch):
    base = 1800000000.0
    monkeypatch.setattr(
        flow.time, "time", lambda: base
    )

    store = StudentOAuthFlowStore(config=config())
    started = store.begin()

    state = parse_qs(
        urlsplit(started.authorization_url).query
    )["state"][0]

    monkeypatch.setattr(
        flow.time,
        "time",
        lambda: base + flow.OAUTH_STATE_COOKIE_MAX_AGE + 1,
    )

    with pytest.raises(PermissionError):
        store.consume(
            state=state,
            browser_cookie=started.state_cookie,
        )


def test_bounded_pending_oauth_capacity():
    store = StudentOAuthFlowStore(
        config=config(), max_flows=1
    )

    store.begin()

    with pytest.raises(RuntimeError, match="capacity"):
        store.begin()


@pytest.mark.parametrize("maximum", [0, -1, 10001, "128"])
def test_invalid_capacity_rejected(maximum):
    with pytest.raises(ValueError):
        StudentOAuthFlowStore(
            config=config(),
            max_flows=maximum,
        )


@pytest.mark.parametrize(
    "redirect",
    [
        "http://chat.example.test/auth/callback",
        "https://chat.example.test/other",
        "https://chat.example.test/auth/callback?next=/",
        "https://attacker@example.test/auth/callback",
        "https://chat.example.test/auth/callback#fragment",
    ],
)
def test_unapproved_redirect_uri_rejected(redirect):
    with pytest.raises(ValueError):
        config(redirect_uri=redirect)


def test_web_and_api_app_ids_must_differ():
    with pytest.raises(ValueError):
        config(web_client_id=API)


def test_default_gateway_still_has_no_oauth_endpoints():
    from src.gateway.app import app

    paths = {route.path for route in app.routes}

    assert "/auth/login" not in paths
    assert "/auth/callback" not in paths
    assert "/api/student/session" not in paths
