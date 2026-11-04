"""Tests for session-bound synthetic plan context."""

import time
from dataclasses import fields
from unittest.mock import patch

import pytest
from mcp.server.auth.provider import AccessToken

from src.gateway.plan_context import PlanContext
from src.gateway.web_sessions import StudentWebSessionStore


ISSUER = "https://issuer.example.invalid/"
TENANT = "synthetic-tenant"


def make_store():
    return StudentWebSessionStore(
        student_lookup={
            (TENANT, "user-a"): "S10001",
            (TENANT, "user-b"): "S10002",
        },
        allowed_issuer=ISSUER,
    )


def issue(store, user):
    token = AccessToken(
        token="synthetic-verified-" + user,
        client_id="synthetic-research-client",
        scopes=["academic.read"],
        expires_at=int(time.time()) + 600,
        resource="synthetic",
        subject=f"{TENANT}:{user}",
        claims={
            "iss": ISSUER,
            "tid": TENANT,
            "oid": user,
        },
    )

    return store.issue(
        verified_access_token=token
    )


def context():
    return PlanContext(
        term_id="2027SP",
        course_ids=("CIS376", "CIS410"),
        avoid_days=("FRI",),
        earliest_start="10:00",
        required_preferences=("avoid_days",),
    )


def test_context_is_bounded_and_structured():
    value = context()

    assert value.course_ids == ("CIS376", "CIS410")
    assert value.avoid_days == ("FRI",)

    assert {item.name for item in fields(value)} == {
        "term_id",
        "course_ids",
        "avoid_days",
        "earliest_start",
        "latest_end",
        "required_preferences",
    }

    assert not hasattr(value, "bearer_token")
    assert not hasattr(value, "messages")
    assert not hasattr(value, "student_record")


@pytest.mark.parametrize("invalid", [
    {"term_id": "2027SP", "course_ids": ()},
    {"term_id": "2027SP", "course_ids": ("BAD",)},
    {"term_id": "2027SP", "course_ids": ("CIS410", "CIS410")},
    {"term_id": "2027XX", "course_ids": ("CIS410",)},
    {"term_id": "2027SP", "course_ids": ("CIS410",),
     "avoid_days": ("FUNDAY",)},
    {"term_id": "2027SP", "course_ids": ("CIS410",),
     "earliest_start": "26:75"},
    {"term_id": "2027SP", "course_ids": ("CIS410",),
     "required_preferences": ("avoid_days",)},
])
def test_invalid_context_is_rejected(invalid):
    with pytest.raises(ValueError):
        PlanContext(**invalid)


def test_context_is_isolated_by_session_and_student():
    store = make_store()
    a = issue(store, "user-a")
    b = issue(store, "user-b")

    store.write_plan_context(
        cookie_value=a.cookie_value,
        context=context(),
    )

    assert store.read_plan_context(
        cookie_value=a.cookie_value,
        term_id="2027SP",
    ) == context()

    assert store.read_plan_context(
        cookie_value=b.cookie_value,
        term_id="2027SP",
    ) is None

    assert store.read_plan_context(
        cookie_value=a.cookie_value,
        term_id="2027FA",
    ) is None


def test_context_survives_csrf_rotation():
    store = make_store()
    a = issue(store, "user-a")

    store.write_plan_context(
        cookie_value=a.cookie_value,
        context=context(),
    )

    new_csrf = store.rotate_csrf(
        cookie_value=a.cookie_value
    )

    assert new_csrf != a.csrf_token

    assert store.read_plan_context(
        cookie_value=a.cookie_value,
        term_id="2027SP",
    ) == context()


def test_context_can_be_cleared_without_revoking_session():
    store = make_store()
    a = issue(store, "user-a")

    store.write_plan_context(
        cookie_value=a.cookie_value,
        context=context(),
    )

    store.clear_plan_context(
        cookie_value=a.cookie_value
    )

    assert store.read_plan_context(
        cookie_value=a.cookie_value,
        term_id="2027SP",
    ) is None

    assert store.resolve(
        cookie_value=a.cookie_value
    ).student_id == "S10001"


def test_logout_revokes_context_with_session():
    store = make_store()
    a = issue(store, "user-a")

    store.write_plan_context(
        cookie_value=a.cookie_value,
        context=context(),
    )

    store.revoke(cookie_value=a.cookie_value)

    assert store.count() == 0

    with pytest.raises(PermissionError):
        store.read_plan_context(
            cookie_value=a.cookie_value,
            term_id="2027SP",
        )


def test_expiration_invalidates_context():
    store = make_store()
    a = issue(store, "user-a")

    store.write_plan_context(
        cookie_value=a.cookie_value,
        context=context(),
    )

    with patch(
        "src.gateway.web_sessions.time.time",
        return_value=a.expires_at + 1,
    ):
        with pytest.raises(PermissionError):
            store.read_plan_context(
                cookie_value=a.cookie_value,
                term_id="2027SP",
            )

    assert store.count() == 0


def test_invalid_cookie_cannot_access_context():
    store = make_store()
    a = issue(store, "user-a")

    store.write_plan_context(
        cookie_value=a.cookie_value,
        context=context(),
    )

    with pytest.raises(PermissionError):
        store.read_plan_context(
            cookie_value="invalid-cookie",
            term_id="2027SP",
        )


def test_unvalidated_context_cannot_be_stored():
    store = make_store()
    a = issue(store, "user-a")

    with pytest.raises(TypeError):
        store.write_plan_context(
            cookie_value=a.cookie_value,
            context={"course_ids": ["CIS410"]},
        )
