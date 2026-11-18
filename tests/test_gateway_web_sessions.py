"""Local-only opaque session-store tests; no real Entra or live browser."""

import time
from mcp.server.auth.provider import AccessToken
import pytest

from src.gateway import web_sessions as web
from src.gateway.web_sessions import (
    StudentWebSessionStore,
)


ISSUER = "https://login.example.test/tenant/v2.0"
LOOKUP = {
    ("tenant-1", "user-a"): "S10001",
    ("tenant-1", "user-b"): "S10002",
}
FAKE_DELEGATED_BEARER = "locally-synthetic-verified-bearer-for-tests"


def trusted_token(
    user="user-a",
    *,
    expires_at=None,
    issuer=ISSUER,
    scope="academic.read",
    token=FAKE_DELEGATED_BEARER,
):
    return AccessToken(
        token=token,
        client_id="research-only-test-client",
        scopes=scope.split() if scope else [],
        expires_at=(
            int(time.time()) + 1800
            if expires_at is None
            else expires_at
        ),
        claims={"iss": issuer, "tid": "tenant-1", "oid": user},
    )


def store(**kwargs):
    return StudentWebSessionStore(
        student_lookup=LOOKUP,
        allowed_issuer=ISSUER,
        **kwargs,
    )


def test_two_students_get_distinct_opaque_sessions():
    sessions = store()
    a = sessions.issue(verified_access_token=trusted_token("user-a"))
    b = sessions.issue(verified_access_token=trusted_token("user-b"))

    assert a.cookie_value != b.cookie_value
    assert a.csrf_token != b.csrf_token
    assert FAKE_DELEGATED_BEARER not in a.cookie_value
    assert FAKE_DELEGATED_BEARER not in b.cookie_value

    verified_a = sessions.resolve(
        cookie_value=a.cookie_value,
        csrf_token=a.csrf_token,
        require_csrf=True,
    )
    verified_b = sessions.resolve(
        cookie_value=b.cookie_value,
        csrf_token=b.csrf_token,
        require_csrf=True,
    )
    assert verified_a.student_id == "S10001"
    assert verified_b.student_id == "S10002"
    assert verified_a.bearer_token == FAKE_DELEGATED_BEARER
    assert verified_b.bearer_token == FAKE_DELEGATED_BEARER
    assert FAKE_DELEGATED_BEARER not in repr(a)
    assert a.cookie_value not in repr(a)
    assert a.csrf_token not in repr(a)
    assert FAKE_DELEGATED_BEARER not in repr(verified_a)


@pytest.mark.parametrize(
    "bad_cookie",
    [None, "", "x", "x" * 500, "not a valid session cookie"],
)
def test_unknown_invalid_or_malformed_session_rejected(bad_cookie):
    sessions = store()
    with pytest.raises(PermissionError):
        sessions.resolve(cookie_value=bad_cookie)


def test_no_csrf_or_incorrect_csrf_denied():
    sessions = store()
    ticket = sessions.issue(verified_access_token=trusted_token())

    for csrf in (None, "", "x" * 43, ticket.cookie_value):
        with pytest.raises(PermissionError, match="CSRF"):
            sessions.resolve(
                cookie_value=ticket.cookie_value,
                csrf_token=csrf,
                require_csrf=True,
            )

    assert sessions.resolve(
        cookie_value=ticket.cookie_value,
        csrf_token=ticket.csrf_token,
        require_csrf=True,
    ).student_id == "S10001"


def test_another_users_csrf_cannot_authorize_request():
    sessions = store()
    a = sessions.issue(verified_access_token=trusted_token("user-a"))
    b = sessions.issue(verified_access_token=trusted_token("user-b"))

    with pytest.raises(PermissionError, match="CSRF"):
        sessions.resolve(
            cookie_value=b.cookie_value,
            csrf_token=a.csrf_token,
            require_csrf=True,
        )


def test_revocation_invalidates_only_selected_session():
    sessions = store()
    a = sessions.issue(verified_access_token=trusted_token("user-a"))
    b = sessions.issue(verified_access_token=trusted_token("user-b"))
    sessions.revoke(cookie_value=a.cookie_value)

    with pytest.raises(PermissionError):
        sessions.resolve(cookie_value=a.cookie_value)
    assert sessions.resolve(cookie_value=b.cookie_value).student_id == (
        "S10002"
    )
    sessions.revoke(cookie_value="non-existent-session")
    assert sessions.count() == 1


def test_session_ttl_clamped_to_token_expiration(monkeypatch):
    base = time.time()
    sessions = store(ttl_seconds=900)
    ticket = sessions.issue(
        verified_access_token=trusted_token(
            expires_at=int(base + 70)
        )
    )
    assert base < ticket.expires_at <= base + 70

    monkeypatch.setattr(web.time, "time", lambda: base + 71)
    with pytest.raises(PermissionError):
        sessions.resolve(cookie_value=ticket.cookie_value)


def test_session_expires_before_valid_bearer_expires(monkeypatch):
    base = time.time()
    sessions = store(ttl_seconds=60)
    ticket = sessions.issue(
        verified_access_token=trusted_token(
            expires_at=int(base + 3600)
        )
    )
    assert base < ticket.expires_at <= base + 60.1
    monkeypatch.setattr(web.time, "time", lambda: base + 62)
    with pytest.raises(PermissionError):
        sessions.resolve(cookie_value=ticket.cookie_value)


@pytest.mark.parametrize(
    "verified",
    [
        None,
        trusted_token("not-mapped"),
        trusted_token(issuer="https://wrong.example/"),
        trusted_token(scope="other.scope"),
        trusted_token(token="bad token"),
        trusted_token(expires_at=1),
    ],
)
def test_unverified_incomplete_or_unmapped_context_denied(verified):
    sessions = store()
    with pytest.raises(PermissionError):
        sessions.issue(verified_access_token=verified)
    assert sessions.count() == 0


def test_missing_expiration_never_gets_browser_session():
    sessions = store()
    candidate = trusted_token()
    candidate.expires_at = None
    with pytest.raises(PermissionError, match="expiring"):
        sessions.issue(verified_access_token=candidate)


def test_session_store_copies_trusted_identity_mapping():
    original = dict(LOOKUP)
    sessions = StudentWebSessionStore(
        student_lookup=original, allowed_issuer=ISSUER
    )
    original[("tenant-1", "user-a")] = "S10002"

    ticket = sessions.issue(verified_access_token=trusted_token("user-a"))
    assert sessions.resolve(
        cookie_value=ticket.cookie_value
    ).student_id == "S10001"


def test_bounded_session_capacity_denies_extra_creation():
    sessions = store(max_sessions=1)
    sessions.issue(verified_access_token=trusted_token("user-a"))
    with pytest.raises(RuntimeError, match="capacity"):
        sessions.issue(verified_access_token=trusted_token("user-b"))


@pytest.mark.parametrize(
    "args",
    [
        {"ttl_seconds": 30},
        {"ttl_seconds": 7200},
        {"max_sessions": 0},
        {"ttl_seconds": "900"},
        {"max_sessions": 1.5},
    ],
)
def test_invalid_security_settings_rejected(args):
    with pytest.raises(ValueError):
        store(**args)


def test_cookie_policy_fails_closed_for_future_https_ui():
    assert web.SESSION_COOKIE_NAME.startswith("__Host-")
    assert web.SESSION_COOKIE_PATH == "/"
    assert web.SESSION_COOKIE_SECURE is True
    assert web.SESSION_COOKIE_HTTPONLY is True
    assert web.SESSION_COOKIE_SAMESITE == "strict"


def test_rotated_csrf_invalidates_previous_csrf():
    sessions = store()
    ticket = sessions.issue(
        verified_access_token=trusted_token()
    )

    new_csrf = sessions.rotate_csrf(
        cookie_value=ticket.cookie_value
    )

    assert new_csrf != ticket.csrf_token

    with pytest.raises(PermissionError, match="CSRF"):
        sessions.resolve(
            cookie_value=ticket.cookie_value,
            csrf_token=ticket.csrf_token,
            require_csrf=True,
        )

    resolved = sessions.resolve(
        cookie_value=ticket.cookie_value,
        csrf_token=new_csrf,
        require_csrf=True,
    )

    assert resolved.student_id == "S10001"


def test_gateway_does_not_expose_session_issuance():
    from src.gateway.app import app

    paths = {route.path for route in app.routes}

    assert "/auth/login" not in paths
    assert "/auth/callback" not in paths
    assert "/api/student/session/chat" not in paths
    assert "/api/student/session" not in paths
