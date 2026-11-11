"""Isolated HTTPS cookie-session route tests.

The test verifier supplies synthetic trusted contexts only.
Cryptographic JWT verification is covered separately by the
existing authenticated MCP HTTP integration suite.
"""

import asyncio
import time
from types import SimpleNamespace

import httpx
import pytest
from mcp.server.auth.provider import AccessToken

from src.gateway.app import create_app
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    StudentWebSessionStore,
)


ORIGIN = "https://chat.example.test"
ISSUER = "https://issuer.example.invalid/"
TENANT = "test-tenant"
USER_A = "test-user-a"
LOOKUP = {(TENANT, USER_A): "S10001"}


class SyntheticVerifier:
    def __init__(self):
        self.enabled = True

    async def verify_token(self, raw):
        if not self.enabled or raw != "verified-test-token-a":
            return None

        return AccessToken(
            token=raw,
            client_id="synthetic-research-client",
            scopes=["academic.read"],
            expires_at=int(time.time()) + 600,
            resource="synthetic",
            subject=f"{TENANT}:{USER_A}",
            claims={
                "iss": ISSUER,
                "tid": TENANT,
                "oid": USER_A,
            },
        )


def test_routes_are_opt_in_and_https_required():
    verifier = SyntheticVerifier()

    async def runner(**kwargs):
        raise AssertionError("Runner must not execute.")

    app = create_app(
        token_verifier=verifier,
        student_lookup=LOOKUP,
        issuer=ISSUER,
        term_id="2027SP",
    )

    paths = {r.path for r in app.routes}

    assert "/api/student/session" not in paths
    assert "/api/student/session/chat" not in paths
    assert "/auth/logout" not in paths
    assert "/auth/login" not in paths
    assert "/auth/callback" not in paths

    store = StudentWebSessionStore(
        student_lookup=LOOKUP,
        allowed_issuer=ISSUER,
    )

    with pytest.raises(ValueError):
        install_browser_session_routes(
            app,
            session_store=store,
            token_verifier=verifier,
            student_lookup=LOOKUP,
            allowed_issuer=ISSUER,
            session_origin="http://chat.example.test",
            term_id="2027SP",
            assistant_runner=runner,
        )

    assert "/api/student/session" not in {
        r.path for r in app.routes
    }


def test_https_session_bootstrap_chat_and_logout():
    async def check():
        verifier = SyntheticVerifier()
        observed = []

        async def runner(**kwargs):
            observed.append(kwargs)
            return SimpleNamespace(
                answer="Option 1: SEC1001 and SEC2002.",
                plan_cards={
                    "schema_version": "leo-team-plan-v1",
                    "status": "proposed_only",
                    "student_id": "S10001",
                    "term_id": "2027SP",
                    "options": [],
                },
                stopped_reason="answered",
                grounded=True,
                mcp_calls=[{"private": "not for browser"}],
            )

        store = StudentWebSessionStore(
            student_lookup=LOOKUP,
            allowed_issuer=ISSUER,
        )

        verified = await verifier.verify_token(
            "verified-test-token-a"
        )
        ticket = store.issue(
            verified_access_token=verified
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

        assert "/auth/login" not in {
            route.path for route in app.routes
        }

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=ORIGIN,
            cookies={
                SESSION_COOKIE_NAME: ticket.cookie_value
            },
        ) as client:
            session = await client.get(
                "/api/student/session"
            )
            assert session.status_code == 200
            assert session.headers["cache-control"] == "no-store"

            body = session.json()
            assert body["authenticated"] is True
            assert body["student_id"] == "S10001"

            csrf = body["csrf_token"]
            assert csrf != ticket.csrf_token
            assert len(csrf) >= 30
            assert "verified-test-token-a" not in session.text

            question = {
                "question": "Plan CIS376 and CIS410"
            }

            missing_origin = await client.post(
                "/api/student/session/chat",
                headers={"X-CSRF-Token": csrf},
                json=question,
            )
            assert missing_origin.status_code == 403

            wrong_origin = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": "https://evil.example.test",
                    "X-CSRF-Token": csrf,
                },
                json=question,
            )
            assert wrong_origin.status_code == 403

            missing_csrf = await client.post(
                "/api/student/session/chat",
                headers={"Origin": ORIGIN},
                json=question,
            )
            assert missing_csrf.status_code == 403

            stale_csrf = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": ticket.csrf_token,
                },
                json=question,
            )
            assert stale_csrf.status_code == 403

            competing_auth = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf,
                    "Authorization": "Bearer another-token",
                },
                json=question,
            )
            assert competing_auth.status_code == 400

            assert observed == []

            authorized = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf,
                },
                json=question,
            )

            assert authorized.status_code == 200
            assert authorized.headers["cache-control"] == "no-store"
            assert authorized.json()["plan_cards"][
                "status"
            ] == "proposed_only"
            assert authorized.json()["plan_cards"][
                "student_id"
            ] == "S10001"
            assert observed[0]["student_id"] == "S10001"
            assert observed[0]["term_id"] == "2027SP"
            assert observed[0]["bearer_token"] == (
                "verified-test-token-a"
            )
            assert "mcp_calls" not in authorized.json()
            assert "verified-test-token-a" not in authorized.text
            assert ticket.cookie_value not in authorized.text

            logged_out = await client.post(
                "/auth/logout",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf,
                },
            )
            assert logged_out.status_code == 200
            assert logged_out.json() == {
                "signed_out": True
            }
            assert store.count() == 0

            after_logout = await client.get(
                "/api/student/session"
            )
            assert after_logout.status_code == 401

    asyncio.run(check())


def test_revoked_verifier_and_cross_origin_get_fail_closed():
    async def check():
        verifier = SyntheticVerifier()
        calls = []

        async def runner(**kwargs):
            calls.append(kwargs)
            raise AssertionError("Must not execute.")

        store = StudentWebSessionStore(
            student_lookup=LOOKUP,
            allowed_issuer=ISSUER,
        )

        token = await verifier.verify_token(
            "verified-test-token-a"
        )
        ticket = store.issue(
            verified_access_token=token
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

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=ORIGIN,
            cookies={
                SESSION_COOKIE_NAME: ticket.cookie_value
            },
        ) as client:
            cross_site = await client.get(
                "/api/student/session",
                headers={
                    "Sec-Fetch-Site": "cross-site",
                },
            )
            assert cross_site.status_code == 403

            verifier.enabled = False

            expired = await client.get(
                "/api/student/session"
            )
            assert expired.status_code == 401

            rejected = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": ticket.csrf_token,
                },
                json={
                    "question": "Plan CIS376"
                },
            )
            assert rejected.status_code == 401
            assert calls == []

    asyncio.run(check())
