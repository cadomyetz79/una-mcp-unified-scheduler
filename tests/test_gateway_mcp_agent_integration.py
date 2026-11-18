"""Signed synthetic identity through gateway, MCP, agent and cards.

No real Entra keys, university records or enrollment operations.
"""

import asyncio
import time
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import httpx2
import jwt

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
from src.mcp_server import team_security as security
from src.mcp_server import team_protected_server as server


TENANT = "11111111-1111-4111-8111-111111111111"
AUDIENCE = "22222222-2222-4222-8222-222222222222"
CLIENT_ID = "33333333-3333-4333-8333-333333333333"
USER_A = "44444444-4444-4444-8444-444444444444"
USER_B = "55555555-5555-4555-8555-555555555555"


def test_signed_gateway_to_real_mcp_and_planner(monkeypatch):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    verifier, issuer, validate_resource = (
        security.select_auth_config(
            tenant_id=TENANT,
            audience=AUDIENCE,
        )
    )

    # This temporary test key replaces external JWKS access.
    monkeypatch.setattr(
        verifier._jwks_client,
        "get_signing_key_from_jwt",
        lambda token: SimpleNamespace(
            key=key.public_key()
        ),
    )

    mappings = {
        (TENANT, USER_A): "S10001",
    }

    monkeypatch.setattr(security, "ISSUER_URL", issuer)
    monkeypatch.setattr(security, "AUTH_TENANT", TENANT)
    monkeypatch.setattr(security, "AUTH_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(
        security,
        "STUDENT_LOOKUP",
        mappings,
    )

    def sign_token(user, *, audience=AUDIENCE, scope="academic.read"):
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
            key,
            algorithm="RS256",
            headers={"kid": "temporary-test-key"},
        )

    # Register the existing protected MCP handlers.
    test_mcp = MCPServer(
        "UNA Gateway Integration Test",
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

    def llm_factory():
        return ScriptedLLM([
            {
                "tool_calls": [
                    call(
                        "plan_schedule",
                        course_ids=["CIS376", "CIS410"],
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

    runner = AuthenticatedSchedulingRunner(
        llm_factory=llm_factory,
        transport=httpx2.ASGITransport(app=mcp_app),
    )

    gateway_app = create_app(
        token_verifier=verifier,
        student_lookup=mappings,
        issuer=issuer,
        term_id="2027SP",
        assistant_runner=runner,
    )

    async def check():
        async with test_mcp.session_manager.run():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(
                    app=gateway_app
                ),
                base_url="http://gateway.test",
            ) as browser:
                token_a = sign_token(USER_A)
                token_b = sign_token(USER_B)

                response = await browser.post(
                    "/api/chat",
                    headers={
                        "Authorization": f"Bearer {token_a}",
                    },
                    json={
                        "question": (
                            "Plan CIS376 and CIS410"
                        ),
                    },
                )

                assert response.status_code == 200, (
                    response.text
                )

                data = response.json()

                assert "SEC1001" in data["answer"]
                assert "SEC2002" in data["answer"]

                cards = data["plan_cards"]
                assert cards is not None
                assert cards["schema_version"] == (
                    "leo-team-plan-v1"
                )
                assert cards["status"] == "proposed_only"
                assert cards["student_id"] == "S10001"
                assert cards["term_id"] == "2027SP"

                assert [
                    section["section_id"]
                    for section
                    in cards["options"][0]["sections"]
                ] == ["SEC1001", "SEC2002"]

                assert response.headers[
                    "cache-control"
                ] == "no-store"

                assert token_a not in response.text
                assert "mcp_calls" not in data
                assert "trace" not in data
                assert "security" not in data

                # A valid signature is not sufficient:
                # user B has no authorized student mapping.
                denied = await browser.post(
                    "/api/chat",
                    headers={
                        "Authorization": f"Bearer {token_b}",
                    },
                    json={
                        "question": (
                            "Plan CIS376 and CIS410"
                        ),
                    },
                )
                assert denied.status_code == 403
                assert "SEC1001" not in denied.text
                assert "SEC2002" not in denied.text

                # STEP_62_NEGATIVE_AUTH_CASES
                question = {
                    "question": "Plan CIS376 and CIS410"
                }

                anonymous = await browser.post(
                    "/api/chat",
                    json=question,
                )
                assert anonymous.status_code == 401

                forged = await browser.post(
                    "/api/chat",
                    headers={
                        "Authorization": "Bearer forged-token",
                    },
                    json=question,
                )
                assert forged.status_code == 401

                wrong_audience = await browser.post(
                    "/api/chat",
                    headers={
                        "Authorization": (
                            "Bearer " + sign_token(
                                USER_A,
                                audience=CLIENT_ID,
                            )
                        ),
                    },
                    json=question,
                )
                assert wrong_audience.status_code == 401

                insufficient_scope = await browser.post(
                    "/api/chat",
                    headers={
                        "Authorization": (
                            "Bearer " + sign_token(
                                USER_A,
                                scope="catalog.read",
                            )
                        ),
                    },
                    json=question,
                )
                assert insufficient_scope.status_code == 401

                injected_identity = await browser.post(
                    "/api/chat",
                    headers={
                        "Authorization": f"Bearer {token_a}",
                    },
                    json={
                        **question,
                        "student_id": "S10002",
                    },
                )
                assert injected_identity.status_code == 422

                # Defense in depth: even a caller that directly
                # invokes the runner with another student's ID
                # must be rejected by protected MCP authorization.
                spoofed_result = await runner(
                    question="Plan CIS376 and CIS410",
                    student_id="S10002",
                    term_id="2027SP",
                    bearer_token=token_a,
                )

                plan_attempts = [
                    entry
                    for entry in spoofed_result.trace
                    if entry.tool == "plan_schedule"
                ]

                assert plan_attempts
                assert all(
                    not entry.ok
                    for entry in plan_attempts
                )
                assert spoofed_result.plan_cards is None

    asyncio.run(check())
