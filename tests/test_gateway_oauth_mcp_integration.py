"""Synthetic OAuth callback -> protected MCP -> verified Leo cards.

The OAuth exchanger and RSA identity keys are test-only.
Protected MCP tools, deterministic planning, and schedule
card projection are the actual unified implementations.

No Microsoft requests, live LLM, Banner access or enrollment.
"""

import asyncio
import base64
import hashlib
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

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
from src.gateway.oauth_flow import (
    OAUTH_STATE_COOKIE,
    StudentOAuthConfig,
    StudentOAuthFlowStore,
)
from src.gateway.oauth_routes import (
    install_browser_oauth_routes,
)
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
API = "22222222-2222-4222-8222-222222222222"
WEB = "33333333-3333-4333-8333-333333333333"
USER = "44444444-4444-4444-8444-444444444444"

ORIGIN = "https://chat.example.test"
TERM = "2027SP"


def test_synthetic_oauth_login_reaches_protected_mcp(monkeypatch):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    verifier, issuer, validate_resource = (
        security.select_auth_config(
            tenant_id=TENANT,
            audience=API,
        )
    )

    monkeypatch.setattr(
        verifier._jwks_client,
        "get_signing_key_from_jwt",
        lambda raw: SimpleNamespace(
            key=private_key.public_key()
        ),
    )

    mappings = {(TENANT, USER): "S10001"}

    monkeypatch.setattr(
        security, "ISSUER_URL", issuer
    )
    monkeypatch.setattr(
        security, "STUDENT_LOOKUP", mappings
    )

    now = int(time.time())

    signed_token = jwt.encode(
        {
            "iss": issuer,
            "aud": API,
            "tid": TENANT,
            "oid": USER,
            "azp": WEB,
            "scp": "academic.read",
            "ver": "2.0",
            "iat": now,
            "nbf": now,
            "exp": now + 1800,
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "local-oauth-mcp-research-key"},
    )

    # Actual protected MCP server, with the existing
    # authorized academic tool handlers.
    test_mcp = MCPServer(
        "UNA Synthetic OAuth MCP Integration",
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
                    )
                ]
            },
            {
                "content": (
                    "Option 1: SEC1001 and SEC2002, "
                    "6 credit hours."
                )
            },
        ])

    real_runner = AuthenticatedSchedulingRunner(
        llm_factory=llm_factory,
        transport=httpx2.ASGITransport(app=mcp_app),
    )

    runner_calls = []

    async def observed_runner(**kwargs):
        runner_calls.append({
            "student_id": kwargs["student_id"],
            "term_id": kwargs["term_id"],
        })
        return await real_runner(**kwargs)

    store = StudentWebSessionStore(
        student_lookup=mappings,
        allowed_issuer=issuer,
    )

    app = create_app(
        token_verifier=verifier,
        student_lookup=mappings,
        issuer=issuer,
        term_id=TERM,
    )

    install_browser_session_routes(
        app,
        session_store=store,
        token_verifier=verifier,
        student_lookup=mappings,
        allowed_issuer=issuer,
        session_origin=ORIGIN,
        term_id=TERM,
        assistant_runner=observed_runner,
    )

    config = StudentOAuthConfig(
        tenant_id=TENANT,
        web_client_id=WEB,
        api_app_id=API,
        redirect_uri=ORIGIN + "/auth/callback",
    )

    flows = StudentOAuthFlowStore(config=config)
    expected = {"challenge": None}
    exchanges = []

    async def fake_code_exchange(
        *, code, code_verifier, redirect_uri
    ):
        # Simulate verification of the PKCE binding
        # in an isolated research code exchanger.
        assert code == "synthetic-research-code"
        assert redirect_uri == config.redirect_uri

        computed = base64.urlsafe_b64encode(
            hashlib.sha256(
                code_verifier.encode("ascii")
            ).digest()
        ).rstrip(b"=").decode("ascii")

        if computed != expected["challenge"]:
            raise PermissionError("PKCE mismatch.")

        exchanges.append(code)
        return signed_token

    install_browser_oauth_routes(
        app,
        flow_store=flows,
        exchange_code=fake_code_exchange,
    )

    async def check():
        async with test_mcp.session_manager.run():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url=ORIGIN,
            ) as browser:

                print("=== VERIFY LOGIN REQUIRED ===")

                before_login = await browser.get(
                    "/api/student/session"
                )
                assert before_login.status_code == 401
                assert store.count() == 0
                assert runner_calls == []

                print("=== START SYNTHETIC OAUTH ===")

                start = await browser.get("/auth/login")

                assert start.status_code == 303
                assert OAUTH_STATE_COOKIE in browser.cookies
                assert SESSION_COOKIE_NAME not in browser.cookies

                target = urlsplit(
                    start.headers["location"]
                )
                values = parse_qs(target.query)

                assert target.hostname == (
                    "login.microsoftonline.com"
                )
                assert values["code_challenge_method"] == [
                    "S256"
                ]
                assert values["scope"] == [
                    f"api://{API}/academic.read"
                ]

                expected["challenge"] = (
                    values["code_challenge"][0]
                )
                state = values["state"][0]

                print("=== FINISH VERIFIED OAUTH CALLBACK ===")

                callback = await browser.get(
                    "/auth/callback",
                    params={
                        "code": "synthetic-research-code",
                        "state": state,
                    },
                )

                assert callback.status_code == 303, (
                    callback.text
                )
                assert callback.headers["location"] == (
                    "/leo/session"
                )

                assert exchanges == [
                    "synthetic-research-code"
                ]
                assert store.count() == 1

                assert SESSION_COOKIE_NAME in browser.cookies
                assert OAUTH_STATE_COOKIE not in browser.cookies

                assert signed_token not in callback.text
                assert signed_token not in (
                    str(browser.cookies)
                )

                print("=== BOOTSTRAP SECURE LEO SESSION ===")

                page = await browser.get("/leo/session")
                assert page.status_code == 200
                assert "una-lion-mark.png" in page.text

                status = await browser.get(
                    "/api/student/session"
                )

                assert status.status_code == 200
                identity = status.json()

                assert identity["authenticated"] is True
                assert identity["student_id"] == "S10001"

                csrf = identity["csrf_token"]
                assert len(csrf) >= 30
                assert signed_token not in status.text

                print("=== VERIFY REQUEST DENIAL ===")

                question = {
                    "question": "Plan CIS376 and CIS410"
                }

                no_csrf = await browser.post(
                    "/api/student/session/chat",
                    headers={"Origin": ORIGIN},
                    json=question,
                )
                assert no_csrf.status_code == 403

                foreign_origin = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": "https://evil.example.test",
                        "X-CSRF-Token": csrf,
                    },
                    json=question,
                )
                assert foreign_origin.status_code == 403

                foreign_student = await browser.post(
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
                assert foreign_student.status_code == 422
                assert runner_calls == []

                print("=== RUN ACTUAL PROTECTED MCP PLANNER ===")

                response = await browser.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                    },
                    json=question,
                )

                assert response.status_code == 200, (
                    response.text
                )

                result = response.json()
                cards = result["plan_cards"]

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

                assert "SEC1001" in result["answer"]
                assert "SEC2002" in result["answer"]

                assert runner_calls == [{
                    "student_id": "S10001",
                    "term_id": TERM,
                }]

                assert signed_token not in response.text
                assert csrf not in response.text

                for hidden in (
                    "security",
                    "mcp_calls",
                    "bearer_token",
                    "internal_trace",
                ):
                    assert hidden not in result

                print("=== REVOKE SESSION ===")

                logout = await browser.post(
                    "/auth/logout",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                    },
                )

                assert logout.status_code == 200
                assert store.count() == 0

                after_logout = await browser.get(
                    "/api/student/session"
                )
                assert after_logout.status_code == 401

                print("=== REJECT CALLBACK REPLAY ===")

                replay = await browser.get(
                    "/auth/callback",
                    params={
                        "code": "synthetic-research-code",
                        "state": state,
                    },
                )

                assert replay.status_code == 401
                assert exchanges == [
                    "synthetic-research-code"
                ]
                assert store.count() == 0
                assert len(runner_calls) == 1

    asyncio.run(check())
