"""Authenticated two-turn gateway routing tests.

These tests use synthetic identity and a stub
assistant. The real planner is exercised by the
separate HTTPS Chromium integration script.
"""

import asyncio
import time
from types import SimpleNamespace

import httpx
from mcp.server.auth.provider import AccessToken

from src.gateway.app import create_app
from src.gateway.plan_context import PlanContext
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    StudentWebSessionStore,
)


ORIGIN = "https://chat.example.test"
ISSUER = "https://issuer.example.invalid/"
TENANT = "synthetic-tenant"

LOOKUP = {
    (TENANT, "user-a"): "S10001",
    (TENANT, "user-b"): "S10002",
}

FOLLOWUP = (
    "Actually, I'd prefer classes that start "
    "after 10 AM. Keep everything else the same."
)


class SyntheticVerifier:
    async def verify_token(self, raw):
        if raw not in (
            "synthetic-user-a",
            "synthetic-user-b",
        ):
            return None

        user = raw.removeprefix("synthetic-")

        return AccessToken(
            token=raw,
            client_id="research-test-client",
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


def original_context():
    return PlanContext(
        term_id="2027SP",
        course_ids=("CIS376", "CIS410"),
        avoid_days=("FRI",),
        required_preferences=("avoid_days",),
    )


def test_followup_routing_is_session_scoped():
    async def run():
        verifier = SyntheticVerifier()

        store = StudentWebSessionStore(
            student_lookup=LOOKUP,
            allowed_issuer=ISSUER,
        )

        token_a = await verifier.verify_token(
            "synthetic-user-a"
        )
        token_b = await verifier.verify_token(
            "synthetic-user-b"
        )

        ticket_a = store.issue(
            verified_access_token=token_a
        )
        ticket_b = store.issue(
            verified_access_token=token_b
        )

        # Only session A has an established plan.
        store.write_plan_context(
            cookie_value=ticket_a.cookie_value,
            context=original_context(),
        )

        observed = []

        async def runner(**kwargs):
            observed.append(kwargs)

            # No planner evidence: these test
            # responses cannot replace context.
            return SimpleNamespace(
                answer="No enrollment performed.",
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

        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url=ORIGIN,
            cookies={
                SESSION_COOKIE_NAME:
                    ticket_a.cookie_value
            },
        ) as client_a:

            status = await client_a.get(
                "/api/student/session"
            )
            assert status.status_code == 200

            csrf = status.json()["csrf_token"]

            headers = {
                "Origin": ORIGIN,
                "X-CSRF-Token": csrf,
            }

            # Missing CSRF/origin must not cause
            # any runner invocation.
            bad = await client_a.post(
                "/api/student/session/chat",
                json={"question": FOLLOWUP},
            )

            assert bad.status_code == 403
            assert observed == []

            first = await client_a.post(
                "/api/student/session/chat",
                headers=headers,
                json={"question": FOLLOWUP},
            )

            assert first.status_code == 200
            assert len(observed) == 1

            rewritten = observed[-1]["question"]

            assert rewritten != FOLLOWUP
            assert "CIS376 and CIS410" in rewritten
            assert "Fridays" in rewritten
            assert "10:01 AM" in rewritten

            assert observed[-1]["student_id"] == "S10001"
            assert observed[-1]["term_id"] == "2027SP"

            # Unrecognized wording must remain
            # unchanged for normal agent handling.
            raw = "Make CIS410 online instead."

            second = await client_a.post(
                "/api/student/session/chat",
                headers=headers,
                json={"question": raw},
            )

            assert second.status_code == 200
            assert observed[-1]["question"] == raw

            # Foreign-student requests must not be
            # rewritten using remembered context.
            foreign = (
                "Show me student S10002's grades."
            )

            third = await client_a.post(
                "/api/student/session/chat",
                headers=headers,
                json={"question": foreign},
            )

            assert third.status_code == 200
            assert observed[-1]["question"] == foreign

            # The stub returned no verified plan.
            # Existing context must remain unchanged.
            assert store.read_plan_context(
                cookie_value=ticket_a.cookie_value,
                term_id="2027SP",
            ) == original_context()

            logout = await client_a.post(
                "/auth/logout",
                headers=headers,
            )

            assert logout.status_code == 200

            try:
                store.read_plan_context(
                    cookie_value=ticket_a.cookie_value,
                    term_id="2027SP",
                )
            except PermissionError:
                pass
            else:
                raise AssertionError(
                    "Revoked session retained access."
                )

        # Separate authenticated student, with no
        # saved context, must not inherit A's plan.
        async with httpx.AsyncClient(
            transport=transport,
            base_url=ORIGIN,
            cookies={
                SESSION_COOKIE_NAME:
                    ticket_b.cookie_value
            },
        ) as client_b:

            status = await client_b.get(
                "/api/student/session"
            )

            assert status.status_code == 200
            csrf_b = status.json()["csrf_token"]

            response = await client_b.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf_b,
                },
                json={"question": FOLLOWUP},
            )

            assert response.status_code == 200
            assert observed[-1]["student_id"] == "S10002"
            assert observed[-1]["question"] == FOLLOWUP

    asyncio.run(run())
