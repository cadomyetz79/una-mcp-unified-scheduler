"""Deterministic concurrent-session regressions; no sleeps or live model."""

import asyncio
from dataclasses import replace
from unittest.mock import patch

import httpx
import pytest

from src.gateway.app import create_app
from src.gateway.session_routes import install_browser_session_routes
from src.gateway.web_sessions import SESSION_COOKIE_NAME, StudentWebSessionStore
from test_gateway_day_continuity import (
    ISSUER, LOOKUP, ORIGIN, SyntheticVerifier, original_context, verified_result,
)
from test_gateway_plan_context import make_store, issue, context


def test_snapshot_revision_detects_clear_and_restore():
    store = make_store()
    ticket = issue(store, "user-a")
    cookie = ticket.cookie_value
    store.write_plan_context(cookie_value=cookie, context=context())
    revision, prior = store.read_plan_snapshot(cookie_value=cookie, term_id="2027SP")
    store.clear_plan_context(cookie_value=cookie)
    store.write_plan_context(cookie_value=cookie, context=prior)
    from src.gateway.web_sessions import StalePlanContextError
    with pytest.raises(StalePlanContextError):
        store.commit_plan_context(
            cookie_value=cookie, expected_revision=revision,
            context=replace(prior, avoid_days=("WED", "FRI")),
        )
    assert store.read_plan_context(cookie_value=cookie, term_id="2027SP") == prior


def test_revision_is_session_scoped_and_survives_csrf_rotation():
    store = make_store()
    a, b = issue(store, "user-a"), issue(store, "user-b")
    revision, prior = store.read_plan_snapshot(
        cookie_value=a.cookie_value, term_id="2027SP",
    )
    assert prior is None
    store.write_plan_context(cookie_value=b.cookie_value, context=context())
    store.rotate_csrf(cookie_value=a.cookie_value)
    store.commit_plan_context(
        cookie_value=a.cookie_value, expected_revision=revision, context=context(),
    )
    updated_revision, updated = store.read_plan_snapshot(
        cookie_value=a.cookie_value, term_id="2027SP",
    )
    assert updated_revision == revision + 1
    assert updated == context()
    store.rotate_csrf(cookie_value=a.cookie_value)
    assert store.read_plan_snapshot(
        cookie_value=a.cookie_value, term_id="2027SP",
    ) == (updated_revision, updated)


async def exercise_race(action, cards=True, seed=True):
    verifier = SyntheticVerifier()
    store = StudentWebSessionStore(student_lookup=LOOKUP, allowed_issuer=ISSUER)
    ticket = store.issue(
        verified_access_token=await verifier.verify_token("synthetic-user-a"),
    )
    if seed:
        store.write_plan_context(cookie_value=ticket.cookie_value, context=original_context())
    started, release = asyncio.Event(), asyncio.Event()

    async def runner(**kwargs):
        if "Mondays" in kwargs["question"]:
            started.set()
            await asyncio.wait_for(release.wait(), timeout=3)
            result = verified_result(["MON", "FRI"])
            result.answer = "STALE_RESULT_MUST_NOT_APPEAR"
            if not cards:
                result.plan_cards = None
            return result
        return verified_result(["WED", "FRI"])

    app = create_app(
        token_verifier=verifier, student_lookup=LOOKUP,
        issuer=ISSUER, term_id="2027SP",
    )
    install_browser_session_routes(
        app, session_store=store, token_verifier=verifier,
        student_lookup=LOOKUP, allowed_issuer=ISSUER,
        session_origin=ORIGIN, term_id="2027SP", assistant_runner=runner,
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url=ORIGIN,
        cookies={SESSION_COOKIE_NAME: ticket.cookie_value},
    ) as client:
        headers = {"Origin": ORIGIN, "X-CSRF-Token": ticket.csrf_token}
        slow = asyncio.create_task(client.post(
            "/api/student/session/chat", headers=headers,
            json={"question": "I can't have classes on Mondays either."},
        ))
        try:
            await asyncio.wait_for(started.wait(), timeout=3)
            if action == "update":
                fast = await client.post(
                    "/api/student/session/chat", headers=headers,
                    json={"question": "I can't have classes on Wednesdays either."},
                )
                assert fast.status_code == 200
                assert fast.json()["plan_cards"] is not None
            elif action == "logout":
                logout = await client.post("/auth/logout", headers=headers)
                assert logout.status_code == 200
            elif action == "clear":
                store.clear_plan_context(cookie_value=ticket.cookie_value)
            if action == "expire":
                with patch("src.gateway.web_sessions.time.time", return_value=10**12):
                    release.set()
                    response = await slow
            else:
                release.set()
                response = await slow
        finally:
            release.set()
            if not slow.done():
                slow.cancel()
            await asyncio.gather(slow, return_exceptions=True)
    assert "STALE_RESULT_MUST_NOT_APPEAR" not in response.text
    if action in ("logout", "expire"):
        assert response.status_code == 401
        with pytest.raises(PermissionError):
            store.read_plan_context(cookie_value=ticket.cookie_value, term_id="2027SP")
    else:
        assert response.status_code == 409
        assert response.json().get("plan_cards") is None
        saved = store.read_plan_context(cookie_value=ticket.cookie_value, term_id="2027SP")
        if action == "clear":
            assert saved is None
        else:
            assert set(saved.avoid_days) == {"WED", "FRI"}


@pytest.mark.parametrize("action", ["update", "logout", "clear", "expire"])
@pytest.mark.parametrize("cards", [True, False])
def test_inflight_result_cannot_outlive_its_context(action, cards):
    asyncio.run(exercise_race(action, cards))


@pytest.mark.parametrize("cards", [True, False])
def test_simultaneous_first_turns_also_detect_conflict(cards):
    asyncio.run(exercise_race("update", cards, seed=False))


@pytest.mark.parametrize("revision", [-1, True, "0", None])
def test_revision_must_be_a_server_integer(revision):
    store = make_store()
    ticket = issue(store, "user-a")
    with pytest.raises(ValueError):
        store.commit_plan_context(
            cookie_value=ticket.cookie_value, expected_revision=revision,
        )


def test_competing_thread_commits_have_exactly_one_winner():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from src.gateway.web_sessions import StalePlanContextError

    store = make_store()
    ticket = issue(store, "user-a")
    revision, _ = store.read_plan_snapshot(
        cookie_value=ticket.cookie_value, term_id="2027SP",
    )
    barrier = Barrier(2)

    def commit(day):
        candidate = replace(context(), avoid_days=(day, "FRI"))
        barrier.wait(timeout=3)
        try:
            store.commit_plan_context(
                cookie_value=ticket.cookie_value, expected_revision=revision,
                context=candidate,
            )
            return candidate
        except StalePlanContextError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(commit, ["MON", "WED"]))
    winners = [result for result in results if result is not None]
    assert len(winners) == 1
    assert store.read_plan_snapshot(
        cookie_value=ticket.cookie_value, term_id="2027SP",
    ) == (revision + 1, winners[0])


def test_cardless_completion_does_not_change_context_revision():
    store = make_store()
    ticket = issue(store, "user-a")
    store.write_plan_context(cookie_value=ticket.cookie_value, context=context())
    snapshot = store.read_plan_snapshot(
        cookie_value=ticket.cookie_value, term_id="2027SP",
    )
    store.commit_plan_context(
        cookie_value=ticket.cookie_value, expected_revision=snapshot[0],
    )
    assert store.read_plan_snapshot(
        cookie_value=ticket.cookie_value, term_id="2027SP",
    ) == snapshot
