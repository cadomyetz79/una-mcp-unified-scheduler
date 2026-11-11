"""LOCAL-ONLY synthetic manual Leo demonstration.

Research-only login with a random local link and a
locally signed synthetic token. This is not an Entra
OAuth flow or a production authentication mechanism.

Browser requests reach a local HTTPS FastAPI server.
The authenticated scheduling runner uses protected MCP,
synthetic Mock Banner, and live Ollama tool selection.

No real accounts, student records or enrollment actions.
Never deploy this synthetic login mechanism.
"""

import asyncio
import ipaddress
import socket
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import secrets
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
# Support direct execution from scripts/.
sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_PATH,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_SAMESITE,
)
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


async def run():
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

        def llm_factory():
            return OllamaLLM(
                model="qwen3:4b-instruct",
                host="http://127.0.0.1:11434",
                timeout=150,
                temperature=0.0,
                think=False,
                num_ctx=8192,
                num_predict=512,
            )

        runner = AuthenticatedSchedulingRunner(
            llm_factory=llm_factory,
            transport=httpx2.ASGITransport(
                app=mcp_app
            ),
        )

        # Local demo: process only one model
        # conversation request at a time.
        model_gate = asyncio.Semaphore(1)

        async def observed_runner(**kwargs):
            if (
                kwargs["student_id"] != "S10001"
                or kwargs["term_id"] != TERM
            ):
                raise PermissionError(
                    "Invalid synthetic student context."
                )

            async with model_gate:
                started = time.monotonic()

                print(
                    "LIVE_MODEL_REQUEST_STARTED",
                    flush=True,
                )

                try:
                    result = await asyncio.wait_for(
                        runner(**kwargs),
                        timeout=240,
                    )
                except asyncio.TimeoutError:
                    print(
                        "LIVE_MODEL_REQUEST_TIMEOUT",
                        flush=True,
                    )
                    return SimpleNamespace(
                        answer=(
                            "The local AI request timed out. "
                            "No verified schedule was returned."
                        ),
                        plan_cards=None,
                        stopped_reason="error",
                        grounded=False,
                    )

                print(
                    "LIVE_MODEL_REQUEST_FINISHED",
                    "seconds=",
                    round(time.monotonic() - started, 2),
                    "model_calls=",
                    result.model_calls,
                    "grounded=",
                    result.grounded,
                    "stop_reason=",
                    result.stopped_reason,
                    flush=True,
                )

                # Fail closed: do not show an
                # unverified model answer as fact.
                if (
                    result.stopped_reason != "answered"
                    or result.grounded is not True
                ):
                    return SimpleNamespace(
                        answer=(
                            "I couldn't verify a complete "
                            "answer from the synthetic "
                            "academic records. No schedule "
                            "was confirmed or enrolled."
                        ),
                        plan_cards=None,
                        stopped_reason="error",
                        grounded=False,
                    )

                cards = result.plan_cards

                print(
                    "VERIFIED_PLAN_CARDS:",
                    (
                        isinstance(cards, dict)
                        and cards.get("status")
                        == "proposed_only"
                        and cards.get("student_id")
                        == "S10001"
                        and cards.get("term_id") == TERM
                    ),
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


        demo_key = secrets.token_urlsafe(24)

        @app.get("/__demo__/login", include_in_schema=False)
        async def synthetic_demo_login(
            request: Request, key: str = ""
        ):
            if (
                request.url.scheme != "https"
                or request.headers.get("host")
                != f"127.0.0.1:{port}"
                or not secrets.compare_digest(
                    key, demo_key
                )
            ):
                raise HTTPException(404, "Not found.")

            # Research-only synthetic JWT, still
            # cryptographically verified by the
            # existing verifier.
            verified = await verifier.verify_token(
                signed_token()
            )

            if verified is None:
                raise HTTPException(
                    503, "Synthetic login unavailable."
                )

            ticket = sessions.issue(
                verified_access_token=verified
            )

            sessions.revoke(
                cookie_value=request.cookies.get(
                    SESSION_COOKIE_NAME
                )
            )

            response = RedirectResponse(
                "/leo/session",
                status_code=303,
            )

            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=ticket.cookie_value,
                max_age=max(
                    1, int(ticket.expires_at - time.time())
                ),
                path=SESSION_COOKIE_PATH,
                secure=SESSION_COOKIE_SECURE,
                httponly=SESSION_COOKIE_HTTPONLY,
                samesite=SESSION_COOKIE_SAMESITE,
            )

            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
            return response

        with tempfile.TemporaryDirectory(
            prefix="una-leo-manual-demo-"
        ) as temp:
            certfile, keyfile = temporary_certificate(
                temp
            )

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

            print()
            print("====================================")
            print(" LEO LIVE OLLAMA RESEARCH DEMO")
            print("====================================")
            print()
            print("Open this URL in Microsoft Edge:")
            print()
            print(
                origin + "/__demo__/login?key="
                + demo_key
            )
            print()
            print("Student: S10001")
            print("Term: 2027SP")
            print("Model: qwen3:4b-instruct")
            print("Local Ollama: http://127.0.0.1:11434")
            print("Try different scheduling questions.")
            print("Example: Plan CIS376 and CIS410")
            print("Example: Avoid Friday classes.")
            print("Each message starts a new agent run.")
            print()
            print("No real Entra login or Banner data.")
            print("No enrollment operations available.")
            print("Keep this terminal open.")
            print("Press Ctrl+C to stop the demo.")
            print()

            async with mcp.session_manager.run():
                try:
                    await webserver.serve(
                        sockets=[listener]
                    )
                finally:
                    listener.close()


if __name__ == "__main__":
    asyncio.run(run())
