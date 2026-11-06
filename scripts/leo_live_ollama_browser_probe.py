"""Actual Chromium -> local HTTPS gateway -> protected MCP demo.

The external identity-provider exchange is simulated offline.
The OAuth code exchanger uses a locally signed synthetic JWT.

Browser session/chat/logout use REAL HTTPS requests to FastAPI.
The protected MCP server and deterministic planner execute
through an isolated in-process ASGI transport.

TEST-ONLY: never enable this fake exchanger in a deployed app.
No real Entra authentication, Banner records, or enrollment.
"""

import asyncio
import argparse
import json
from dataclasses import asdict
import ipaddress
import socket
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx2
import jwt
import pytest
import uvicorn
from cryptography import x509
from cryptography.hazmat.primitives import (
    hashes, serialization,
)
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from mcp.server import MCPServer
from mcp.server.auth.settings import AuthSettings
from playwright.async_api import async_playwright, expect
from pydantic import AnyHttpUrl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai-agent"))

from agent.llm import OllamaLLM
from src.gateway.app import create_app
from src.gateway.oauth_flow import (
    StudentOAuthConfig, StudentOAuthFlowStore,
)
from src.gateway.oauth_routes import install_browser_oauth_routes
from src.gateway.runner import AuthenticatedSchedulingRunner
from src.gateway.session_routes import install_browser_session_routes
from src.gateway.web_sessions import StudentWebSessionStore
from src.mcp_server import team_security as security
from src.mcp_server import team_protected_server as server


TENANT = "11111111-1111-4111-8111-111111111111"
API = "22222222-2222-4222-8222-222222222222"
WEB = "33333333-3333-4333-8333-333333333333"
USER = "44444444-4444-4444-8444-444444444444"
TERM = "2027SP"


def temporary_certificate(folder):
    """Create an ephemeral self-signed certificate for 127.0.0.1."""
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048,
    )

    subject = x509.Name([
        x509.NameAttribute(
            NameOID.COMMON_NAME, "127.0.0.1"
        )
    ])

    now = datetime.now(timezone.utc)

    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=2))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.IPAddress(
                    ipaddress.ip_address("127.0.0.1")
                )
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    keyfile = Path(folder) / "local-test-key.pem"
    certfile = Path(folder) / "local-test-cert.pem"

    keyfile.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))

    certfile.write_bytes(certificate.public_bytes(
        serialization.Encoding.PEM
    ))

    keyfile.chmod(0o600)

    return str(certfile), str(keyfile)


async def run(*, continuity=False, evidence=None, screenshot_path=None):
    records = []
    results = []
    with pytest.MonkeyPatch.context() as mp:
        signing_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048,
        )

        verifier, issuer, resource_validator = (
            security.select_auth_config(
                tenant_id=TENANT,
                audience=API,
            )
        )

        mp.setattr(
            verifier._jwks_client,
            "get_signing_key_from_jwt",
            lambda raw: SimpleNamespace(
                key=signing_key.public_key()
            ),
        )

        student_lookup = {(TENANT, USER): "S10001"}
        mp.setattr(security, "ISSUER_URL", issuer)
        mp.setattr(security, "AUTH_TENANT", TENANT)
        mp.setattr(security, "AUTH_AUDIENCE", API)
        mp.setattr(
            security, "STUDENT_LOOKUP", student_lookup
        )

        def signed_token():
            now = int(time.time())
            return jwt.encode(
                {
                    "iss": issuer,
                    "aud": API,
                    "tid": TENANT,
                    "oid": USER,
                    "azp": WEB,
                    "scp": "academic.read",
                    "roles": ["RAG.Student"],
                    "ver": "2.0",
                    "iat": now,
                    "nbf": now,
                    "exp": now + 900,
                },
                signing_key,
                algorithm="RS256",
                headers={"kid": "local-browser-test-key"},
            )

        mcp = MCPServer(
            "UNA Local HTTPS Research Browser Test",
            token_verifier=verifier,
            auth=AuthSettings(
                issuer_url=AnyHttpUrl(issuer),
                resource_server_url=AnyHttpUrl(
                    security.RESOURCE_URL
                ),
                required_scopes=["academic.read"],
                validate_token_resource=resource_validator,
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
            mcp.tool()(handler)

        mcp_app = mcp.streamable_http_app(
            streamable_http_path="/mcp",
            stateless_http=True,
            json_response=True,
        )

        live_models = []

        def llm_factory():
            model = OllamaLLM(
                model="qwen3:4b-instruct",
                host="http://127.0.0.1:11434",
                timeout=150,
                temperature=0.0,
                think=False,
                num_ctx=8192,
                num_predict=512,
            )
            live_models.append(model)
            return model

        runner = AuthenticatedSchedulingRunner(
            llm_factory=llm_factory,
            transport=httpx2.ASGITransport(
                app=mcp_app
            ),
        )

        calls = []

        async def observed_runner(**kwargs):
            calls.append({
                "student_id": kwargs["student_id"],
                "term_id": kwargs["term_id"],
            })
            result = await runner(**kwargs)
            results.append(result)
            records.append({
                "turn": len(results),
                "model_calls": len(live_models[-1].stats),
                "stopped_reason": result.stopped_reason,
                "grounded": result.grounded,
                "runner_cards": result.plan_cards is not None,
                "plans": [
                    {
                        "ok": entry.ok,
                        "requested": entry.result.get("requested"),
                        "preferences_applied": entry.result.get("preferences_applied"),
                        "option_count": len(entry.result.get("options", [])),
                        "options": [
                            [{"course_id": section["course_id"],
                              "section_id": section["section_id"],
                              "meeting_days": [
                                  day for meeting in section["meetings"]
                                  for day in meeting["days"]
                              ]}
                             for section in option["sections"]]
                            for option in entry.result.get("options", [])
                        ],
                        "exclusions": [
                            {"course_id": item["course_id"], "code": item["code"]}
                            for item in entry.result.get("excluded", [])
                        ],
                    }
                    for entry in result.trace
                    if entry.tool == "plan_schedule" and isinstance(entry.result, dict)
                ],
            })
            if evidence is not None:
                evidence["turns"] = records
            if continuity and len(results) > 1:
                return result

            model_plans = [
                entry
                for entry in result.trace
                if entry.tool == "plan_schedule"
                and entry.by == "model"
                and entry.ok
            ]

            print(
                "LIVE_MODEL_CALLS:",
                len(live_models[-1].stats),
                flush=True,
            )
            print(
                "AGENT_STOP_REASON:",
                result.stopped_reason,
                flush=True,
            )
            print(
                "SUCCESSFUL_MODEL_PLAN_CALLS:",
                len(model_plans),
                flush=True,
            )

            assert model_plans, (
                "The live model did not successfully "
                "select and execute plan_schedule."
            )

            assert result.stopped_reason == "answered"
            assert result.grounded is True

            cards = result.plan_cards
            assert isinstance(cards, dict)
            assert cards.get("student_id") == "S10001"
            assert cards.get("term_id") == TERM
            assert cards.get("status") == "proposed_only"

            print(
                "LIVE_OLLAMA_MCP_PLANNING_VERIFIED",
                flush=True,
            )

            return result

        sessions = StudentWebSessionStore(
            student_lookup=student_lookup,
            allowed_issuer=issuer,
        )

        # Bind the HTTPS server strictly to loopback.
        listener = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        listener.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        listener.setblocking(False)

        port = listener.getsockname()[1]
        origin = f"https://127.0.0.1:{port}"

        app = create_app(
            token_verifier=verifier,
            student_lookup=student_lookup,
            issuer=issuer,
            term_id=TERM,
        )

        install_browser_session_routes(
            app,
            session_store=sessions,
            token_verifier=verifier,
            student_lookup=student_lookup,
            allowed_issuer=issuer,
            session_origin=origin,
            term_id=TERM,
            assistant_runner=observed_runner,
        )

        oauth_config = StudentOAuthConfig(
            tenant_id=TENANT,
            web_client_id=WEB,
            api_app_id=API,
            redirect_uri=origin + "/auth/callback",
        )

        oauth_flows = StudentOAuthFlowStore(
            config=oauth_config
        )

        expected = {
            "challenge": None,
            "idp_interceptions": 0,
            "exchanges": 0,
        }

        async def fake_code_exchange(
            *, code, code_verifier, redirect_uri
        ):
            import base64
            import hashlib

            assert code == "local-synthetic-code"
            assert redirect_uri == oauth_config.redirect_uri

            challenge = base64.urlsafe_b64encode(
                hashlib.sha256(
                    code_verifier.encode("ascii")
                ).digest()
            ).rstrip(b"=").decode("ascii")

            if challenge != expected["challenge"]:
                raise PermissionError("PKCE mismatch.")

            expected["exchanges"] += 1
            return signed_token()

        install_browser_oauth_routes(
            app,
            flow_store=oauth_flows,
            exchange_code=fake_code_exchange,
        )

        with tempfile.TemporaryDirectory(
            prefix="una-leo-https-test-"
        ) as temp:
            certfile, keyfile = temporary_certificate(temp)

            config = uvicorn.Config(
                app,
                host="127.0.0.1",
                port=port,
                ssl_certfile=certfile,
                ssl_keyfile=keyfile,
                proxy_headers=False,
                log_level="warning",
                access_log=False,
            )

            webserver = uvicorn.Server(config)

            print("=== START LOOPBACK HTTPS GATEWAY ===")

            async with mcp.session_manager.run():
                task = asyncio.create_task(
                    webserver.serve(sockets=[listener])
                )

                try:
                    for _ in range(100):
                        if webserver.started:
                            break
                        if task.done():
                            await task
                            raise RuntimeError(
                                "HTTPS gateway stopped early."
                            )
                        await asyncio.sleep(0.1)

                    assert webserver.started, (
                        "HTTPS gateway failed to start."
                    )

                    # Diagnostic only: test HTTPS independently
                    # before launching Chromium.
                    print("=== LOCAL HTTPS CONNECTIVITY CHECK ===")

                    import httpx

                    async with httpx.AsyncClient(
                        verify=False,
                        trust_env=False,
                        timeout=8.0,
                    ) as probe:
                        response = await probe.get(
                            origin + "/leo/session"
                        )

                    print(
                        "LOOPBACK_HTTPS_STATUS",
                        response.status_code,
                    )
                    assert response.status_code == 200, (
                        "Local HTTPS gateway did not serve Leo."
                    )

                    print("LOOPBACK_HTTPS_GATEWAY_REACHABLE")

                    async with async_playwright() as p:
                        browser = await p.chromium.launch(
                            headless=True
                        )

                        context = await browser.new_context(
                            ignore_https_errors=True,
                            viewport={
                                "width": 1440,
                                "height": 900,
                            },
                        )

                        page = await context.new_page()
                        page.set_default_timeout(180000)
                        errors = []

                        page.on(
                            "requestfailed",
                            lambda request: print(
                                "BROWSER_REQUEST_FAILED",
                                urlsplit(request.url).path,
                                request.failure,
                            ),
                        )

                        page.on(
                            "response",
                            lambda response: print(
                                "BROWSER_HTTP_RESPONSE",
                                response.status,
                                urlsplit(response.url).path,
                            )
                            if urlsplit(response.url).netloc
                            == f"127.0.0.1:{port}"
                            else None,
                        )

                        page.on(
                            "pageerror",
                            lambda error: errors.append(
                                str(error)
                            ),
                        )

                        # Block any external navigation or API
                        # traffic. Only the local HTTPS gateway
                        # may be contacted directly.
                        async def local_only(route):
                            target = urlsplit(
                                route.request.url
                            )

                            if (
                                target.scheme == "https"
                                and target.netloc
                                == f"127.0.0.1:{port}"
                            ):
                                return await route.continue_()

                            return await route.abort(
                                "blockedbyclient"
                            )

                        await context.route(
                            "**/*", local_only
                        )

                        # External requests remain blocked.
                        # The test inspects the OAuth URL
                        # without visiting Microsoft.

                        try:
                            print(
                                "=== VERIFY SIGN-IN REQUIRED ==="
                            )

                            await page.goto(
                                origin + "/leo/session",
                                wait_until="domcontentloaded",
                            )

                            await expect(
                                page.locator(
                                    "#session-status"
                                )
                            ).to_contain_text(
                                "Not signed in"
                            )

                            assert sessions.count() == 0

                            print(
                                "=== SIMULATE OFFLINE IDP APPROVAL ==="
                            )

                            login = await context.request.get(
                                origin + "/auth/login",
                                max_redirects=0,
                            )

                            assert login.status == 303

                            authorization = urlsplit(
                                login.headers["location"]
                            )

                            assert authorization.scheme == "https"
                            assert authorization.netloc == (
                                "login.microsoftonline.com"
                            )
                            assert authorization.path == (
                                f"/{TENANT}/oauth2/v2.0/authorize"
                            )

                            values = parse_qs(
                                authorization.query
                            )

                            assert values["client_id"] == [WEB]
                            assert values["response_type"] == ["code"]
                            assert values["redirect_uri"] == [
                                oauth_config.redirect_uri
                            ]
                            assert values["code_challenge_method"] == [
                                "S256"
                            ]
                            assert values["scope"] == [
                                f"api://{API}/academic.read"
                            ]

                            expected["challenge"] = (
                                values["code_challenge"][0]
                            )

                            # Test-only simulation of IDP approval.
                            # No HTTP request to Microsoft occurs.
                            expected["idp_interceptions"] += 1

                            # Chromium now visits the REAL local
                            # HTTPS callback using the shared cookie.
                            await page.goto(
                                origin + "/auth/callback?"
                                + urlencode({
                                    "state": values["state"][0],
                                    "code": "local-synthetic-code",
                                }),
                                wait_until="domcontentloaded",
                            )

                            await expect(
                                page.locator(
                                    "#session-status"
                                )
                            ).to_contain_text(
                                "Signed in: S10001"
                            )

                            assert (
                                expected["idp_interceptions"]
                                == 1
                            )
                            assert expected["exchanges"] == 1
                            assert sessions.count() == 1

                            cookies = await context.cookies(
                                origin
                            )

                            session_cookie = next(
                                c for c in cookies
                                if c["name"] ==
                                "__Host-una_student_session"
                            )

                            assert session_cookie["secure"]
                            assert session_cookie["httpOnly"]
                            assert (
                                session_cookie["sameSite"]
                                == "Strict"
                            )

                            assert await page.locator(
                                "img[data-brand-lion]"
                            ).evaluate(
                                "(img) => img.complete "
                                "&& img.naturalWidth > 0"
                            )

                            print(
                                "=== REAL HTTPS CHAT TO MCP ==="
                            )

                            await page.locator(
                                "#message"
                            ).fill(
                                "Plan CIS376 and CIS410. I can't have classes on Fridays."
                                if continuity else "Plan CIS376 and CIS410"
                            )

                            await page.locator(
                                "#send"
                            ).click()

                            await expect(
                                page.locator(
                                    ".verified-section"
                                )
                            ).to_have_count(
                                2, timeout=180000
                            )

                            await expect(
                                page.locator(
                                    "#feedback"
                                )
                            ).to_contain_text(
                                "Nothing was enrolled"
                            )

                            assert calls == [{
                                "student_id": "S10001",
                                "term_id": TERM,
                            }]

                            assert await page.get_by_text(
                                "CIS376 · SEC1001"
                            ).is_visible()

                            assert await page.get_by_text(
                                "CIS410 · SEC2002"
                            ).is_visible()

                            if continuity:
                                saved = sessions.read_plan_context(
                                    cookie_value=session_cookie["value"], term_id=TERM,
                                )
                                assert saved is not None
                                assert set(saved.avoid_days) == {"FRI"}
                                assert saved.required_preferences == ("avoid_days",)
                                evidence["initial_context"] = asdict(saved)
                                followups = [
                                    "Actually, I'd prefer classes that start after 10 AM. "
                                    "Keep everything else the same.",
                                    "Actually, I can't have classes on Wednesdays either. "
                                    "Keep everything else the same.",
                                ]
                                for index, question in enumerate(followups, start=2):
                                    async with page.expect_response(
                                        lambda response: urlsplit(response.url).path
                                        == "/api/student/session/chat",
                                        timeout=600000,
                                    ) as pending:
                                        await page.locator("#message").fill(question)
                                        await page.locator("#send").click()
                                    response = await pending.value
                                    payload = await response.json()
                                    record = records[-1]
                                    record["http_status"] = response.status
                                    record["browser_cards"] = payload.get("plan_cards") is not None
                                    updated = sessions.read_plan_context(
                                        cookie_value=session_cookie["value"], term_id=TERM,
                                    )
                                    record["saved_context"] = asdict(updated) if updated else None
                                    assert response.status == 200
                                    assert record["plans"]
                                    expected_days = {"FRI"} if index == 2 else {"FRI", "WED"}
                                    for plan in record["plans"]:
                                        assert plan["ok"]
                                        assert plan["requested"] == ["CIS376", "CIS410"]
                                        prefs = plan["preferences_applied"]
                                        assert set(prefs["avoid_days"]) == expected_days
                                        assert prefs["required"] == ["avoid_days"]
                                        assert prefs["earliest_start"] == "10:01"
                                    if index == 2:
                                        assert record["browser_cards"]
                                        assert updated.earliest_start == "10:01"
                                        saved = updated
                                    else:
                                        # Partial plans are supported: CIS376 is
                                        # excluded because its alternative is full.
                                        assert record["browser_cards"]
                                        assert record["grounded"]
                                        assert len(record["plans"]) == 1
                                        for plan in record["plans"]:
                                            assert plan["exclusions"] == [{
                                                "course_id": "CIS376",
                                                "code": "NO_SECTION_MATCHES_PREFERENCES",
                                            }]
                                            assert plan["options"]
                                            for option in plan["options"]:
                                                assert [s["course_id"] for s in option] == ["CIS410"]
                                                for section in option:
                                                    assert not expected_days.intersection(
                                                        section["meeting_days"]
                                                    )
                                        assert "CIS376" in payload["answer"]
                                        assert updated.course_ids == ("CIS376", "CIS410")
                                        assert set(updated.avoid_days) == expected_days
                                        assert updated.earliest_start == "10:01"
                                        assert updated.required_preferences == ("avoid_days",)
                                        await expect(page.locator(".assistant-entry")).to_have_count(3)
                                        await expect(
                                            page.locator(".assistant-entry").last
                                        ).to_contain_text("CIS376")
                                        await expect(
                                            page.locator(".assistant-entry").last.locator(
                                                ".verified-section"
                                            )
                                        ).to_have_count(1)
                                        evidence["partial_proposal_verified"] = True
                                    print("CONTINUITY_TURN", json.dumps(record), flush=True)

                            screenshot = screenshot_path or (
                                ROOT / "docs/evidence/" / (
                                    "2026-11-04-step133-continuity.png" if continuity else
                                    "2026-11-03-step95-live-ollama-browser-mcp.png"
                                )
                            )

                            screenshot.parent.mkdir(
                                parents=True,
                                exist_ok=True,
                            )

                            await page.screenshot(
                                path=str(screenshot),
                                full_page=True,
                            )

                            print(
                                "LEO_BROWSER_HTTPS_MCP_CARDS_VERIFIED"
                            )

                            print(
                                "=== VERIFY REAL SESSION LOGOUT ==="
                            )

                            await page.locator(
                                "#sign-out"
                            ).click()

                            await expect(
                                page.locator(
                                    "#session-status"
                                )
                            ).to_contain_text(
                                "Signed out"
                            )

                            assert sessions.count() == 0

                            await page.reload(
                                wait_until="domcontentloaded"
                            )

                            await expect(
                                page.locator(
                                    "#session-status"
                                )
                            ).to_contain_text(
                                "Not signed in"
                            )

                            assert len(calls) == (3 if continuity else 1)
                            if evidence is not None:
                                evidence["session_revoked"] = sessions.count() == 0
                            assert not errors, errors

                            print(
                                "LEO_BROWSER_SESSION_REVOCATION_VERIFIED"
                            )
                            print(
                                "STEP_95_LIVE_OLLAMA_BROWSER_MCP_PASSED"
                            )

                        finally:
                            await context.close()
                            await browser.close()

                finally:
                    webserver.should_exit = True

                    try:
                        await asyncio.wait_for(
                            task, timeout=15
                        )
                    except asyncio.TimeoutError:
                        task.cancel()
                        await asyncio.gather(
                            task,
                            return_exceptions=True,
                        )

                    listener.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuity-evidence", type=Path)
    args = parser.parse_args()
    if args.continuity_evidence is not None and (
        args.continuity_evidence.exists()
        or args.continuity_evidence.with_suffix(".png").exists()
    ):
        parser.error("Use a new evidence filename; existing research evidence is preserved.")
    evidence = {
        "schema_version": "leo-live-continuity-v1",
        "model": "qwen3:4b-instruct",
        "temperature": 0.0,
        "synthetic_identity_and_banner": True,
        "passed": False,
    }
    try:
        asyncio.run(run(
            continuity=args.continuity_evidence is not None,
            evidence=evidence,
            screenshot_path=(
                args.continuity_evidence.with_suffix(".png")
                if args.continuity_evidence is not None else None
            ),
        ))
        evidence["passed"] = True
    finally:
        if args.continuity_evidence is not None:
            args.continuity_evidence.parent.mkdir(parents=True, exist_ok=True)
            args.continuity_evidence.write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8",
            )
