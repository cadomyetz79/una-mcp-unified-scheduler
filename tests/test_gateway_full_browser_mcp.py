"""Signed browser session -> protected MCP -> real planner -> Leo cards.

This uses local RSA keys, synthetic student records, existing protected
MCP tool handlers, and the actual deterministic scheduling implementation.

No Microsoft service, real student record, live LLM, or enrollment action.
No browser login or session issuance endpoint is created.
"""

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import httpx
import httpx2
import jwt
import pytest

from cryptography.hazmat.primitives.asymmetric import rsa
from mcp.server import MCPServer
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "ai-agent"),
)

from agent.llm import ScriptedLLM, call

from src.gateway.app import create_app
from src.gateway.runner import AuthenticatedSchedulingRunner
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    StudentWebSessionStore,
)

from src.mcp_server import team_security as security
from src.mcp_server import team_protected_server as server


TENANT = "11111111-1111-4111-8111-111111111111"
AUDIENCE = "22222222-2222-4222-8222-222222222222"
CLIENT_ID = "33333333-3333-4333-8333-333333333333"
USER_A = "44444444-4444-4444-8444-444444444444"
USER_B = "55555555-5555-4555-8555-555555555555"

ORIGIN = "https://chat.example.test"
TERM = "2027SP"


def test_signed_browser_session_reaches_real_mcp_planner(monkeypatch):
    """Verify successful planning and denial before MCP execution."""

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    verifier, issuer, validate_resource = (
        security.select_auth_config(
            tenant_id=TENANT,
            audience=AUDIENCE,
        )
    )

    # Cryptographic validation uses the local test RSA key.
    # This replaces external Microsoft JWKS retrieval only in this test.
    monkeypatch.setattr(
        verifier._jwks_client,
        "get_signing_key_from_jwt",
        lambda raw: SimpleNamespace(
            key=private_key.public_key()
        ),
    )

    mappings = {
        (TENANT, USER_A): "S10001",
    }

    monkeypatch.setattr(
        security, "ISSUER_URL", issuer
    )
    monkeypatch.setattr(security, "AUTH_TENANT", TENANT)
    monkeypatch.setattr(security, "AUTH_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(
        security, "STUDENT_LOOKUP", mappings
    )

    def sign_token(
        user,
        *,
        audience=AUDIENCE,
        scope="academic.read",
    ):
        now = int(time.time())

        return jwt.encode(
            {
                "iss": issuer,
                "aud": audience,
                "tid": TENANT,
                "oid": user,
                "azp": CLIENT_ID,
                "scp": scope,
                "roles": ["RAG.Student"],
                "ver": "2.0",
                "iat": now,
                "nbf": now,
                "exp": now + 1800,
            },
            private_key,
            algorithm="RS256",
            headers={
                "kid": "synthetic-browser-mcp-test-key"
            },
        )

    # Construct the real protected MCP server using the
    # same six handlers as the earlier gateway integration.
    test_mcp = MCPServer(
        "UNA Browser Session MCP Integration Test",
        token_verifier=verifier,
        auth=AuthSettings(
            issuer_url=AnyHttpUrl(issuer),
            resource_server_url=AnyHttpUrl(
                security.RESOURCE_URL
            ),
            required_scopes=["academic.read"],
            validate_token_resource=validate_resource,
        ),
    )

    for handler in (
        server.get_student_record,
        server.get_course_history,
        server.get_course,
        server.search_courses,
        server.get_course_sections,
        server.get_student_enrollments,
    ):
        test_mcp.tool()(handler)

    mcp_app = test_mcp.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )

    # Deterministic script chooses the scheduling tool.
    # The planner, MCP authorization, and cards are real.
    def llm_factory():
        return ScriptedLLM([
            {
                "tool_calls": [
                    call(
                        "plan_schedule",
                        course_ids=[
                            "CIS376",
                            "CIS410",
                        ],
                    ),
                ],
            },
            {
                "content": (
                    "Option 1: SEC1001 and SEC2002, "
                    "6 credit hours."
                ),
            },
        ])

    real_runner = AuthenticatedSchedulingRunner(
        llm_factory=llm_factory,
        transport=httpx2.ASGITransport(app=mcp_app),
    )

    # Count actual runner entries. Denied browser
    # requests must not reach MCP or the planner.
    runner_calls = []

    async def observed_runner(**kwargs):
        runner_calls.append({
            "student_id": kwargs["student_id"],
            "term_id": kwargs["term_id"],
        })
        return await real_runner(**kwargs)

    session_store = StudentWebSessionStore(
        student_lookup=mappings,
        allowed_issuer=issuer,
    )

    gateway = create_app(
        token_verifier=verifier,
        student_lookup=mappings,
        issuer=issuer,
        term_id=TERM,
    )

    install_browser_session_routes(
        gateway,
        session_store=session_store,
        token_verifier=verifier,
        student_lookup=mappings,
        allowed_issuer=issuer,
        session_origin=ORIGIN,
        term_id=TERM,
        assistant_runner=observed_runner,
    )

    async def check():
        # The access token is cryptographically verified
        # BEFORE the trusted test harness issues a session.
        token_a = sign_token(USER_A)
        verified_a = await verifier.verify_token(token_a)

        assert verified_a is not None

        ticket = session_store.issue(
            verified_access_token=verified_a
        )

        assert session_store.count() == 1
        assert token_a not in ticket.cookie_value
        assert ticket.cookie_value not in repr(ticket)

        # Correctly signed but unmapped identity cannot
        # receive an academic browser session.
        token_b = sign_token(USER_B)
        verified_b = await verifier.verify_token(token_b)

        assert verified_b is not None

        with pytest.raises(PermissionError):
            session_store.issue(
                verified_access_token=verified_b
            )

        # Invalid audience or academic scope is denied
        # before any session can be created.
        assert await verifier.verify_token(
            sign_token(USER_A, audience=CLIENT_ID)
        ) is None

        assert await verifier.verify_token(
            sign_token(USER_A, scope="catalog.read")
        ) is None

        assert session_store.count() == 1

        async with test_mcp.session_manager.run():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(
                    app=gateway
                ),
                base_url=ORIGIN,
                cookies={
                    SESSION_COOKIE_NAME:
                        ticket.cookie_value,
                },
            ) as browser:

                # Loading the page itself gives no
                # permission to access academic data.
                page = await browser.get("/leo/session")

                assert page.status_code == 200
                assert "una-lion-mark.png" in page.text
                assert "leo-team-plan-v1" not in page.text
                assert token_a not in page.text

                # Browser session bootstrap:
                # verifies the delegated JWT and
                # rotates the CSRF secret.
                status = await browser.get(
                    "/api/student/session"
                )

                assert status.status_code == 200
                assert status.headers[
                    "cache-control"
                ] == "no-store"

                data = status.json()

                assert data["authenticated"] is True
                assert data["student_id"] == "S10001"

                csrf = data["csrf_token"]

                assert csrf != ticket.csrf_token
                assert len(csrf) >= 30
                assert token_a not in status.text

                question = {
                    "question": "Plan CIS376 and CIS410"
                }

                # No valid CSRF token.
                no_csrf = await browser.post(
                    "/api/student/session/chat",
                    headers={"Origin": ORIGIN},
                    json=question,
                )

                assert no_csrf.status_code == 403

                # Previous CSRF token must no longer work.
                stale_csrf = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token":
                            ticket.csrf_token,
                    },
                    json=question,
                )

                assert stale_csrf.status_code == 403

                # Foreign origins cannot invoke the agent.
                cross_origin = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": "https://evil.example.test",
                        "X-CSRF-Token": csrf,
                    },
                    json=question,
                )

                assert cross_origin.status_code == 403

                # Browser may not override the bound identity.
                injected_student = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                    },
                    json={
                        **question,
                        "student_id": "S10002",
                    },
                )

                assert injected_student.status_code == 422

                # Do not mix cookie and bearer authentication.
                competing_bearer = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                        "Authorization":
                            f"Bearer {token_b}",
                    },
                    json=question,
                )

                assert competing_bearer.status_code == 400

                assert runner_calls == []

                # ACTUAL END-TO-END INTEGRATION:
                # HTTPS session -> verifier -> runner ->
                # protected MCP -> deterministic planner ->
                # verified Leo plan cards.
                result = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                    },
                    json=question,
                )

                assert result.status_code == 200, (
                    result.text
                )

                response = result.json()

                assert "SEC1001" in response["answer"]
                assert "SEC2002" in response["answer"]

                cards = response["plan_cards"]

                assert cards is not None
                assert cards["schema_version"] == (
                    "leo-team-plan-v1"
                )
                assert cards["status"] == "proposed_only"
                assert cards["student_id"] == "S10001"
                assert cards["term_id"] == TERM

                sections = cards["options"][0]["sections"]

                assert [
                    section["section_id"]
                    for section in sections
                ] == ["SEC1001", "SEC2002"]

                assert runner_calls == [{
                    "student_id": "S10001",
                    "term_id": TERM,
                }]

                # Browser never receives delegated
                # bearer credentials or internal traces.
                for secret in (
                    token_a,
                    token_b,
                    ticket.cookie_value,
                    csrf,
                ):
                    assert secret not in result.text

                for internal_field in (
                    "trace",
                    "mcp_calls",
                    "security",
                    "bearer_token",
                ):
                    assert internal_field not in response

                assert result.headers[
                    "cache-control"
                ] == "no-store"

                # Bootstrap rotates CSRF again.
                refreshed = await browser.get(
                    "/api/student/session"
                )

                assert refreshed.status_code == 200

                next_csrf = refreshed.json()[
                    "csrf_token"
                ]

                assert next_csrf != csrf

                old_csrf = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                    },
                    json=question,
                )

                assert old_csrf.status_code == 403
                assert len(runner_calls) == 1

                # Revoke the browser session.
                logout = await browser.post(
                    "/auth/logout",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": next_csrf,
                    },
                )

                assert logout.status_code == 200
                assert logout.json() == {
                    "signed_out": True
                }

                assert session_store.count() == 0

                after_logout = await browser.get(
                    "/api/student/session"
                )

                assert after_logout.status_code == 401
                assert len(runner_calls) == 1

    asyncio.run(check())
