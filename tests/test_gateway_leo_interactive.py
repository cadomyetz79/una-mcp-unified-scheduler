"""Original Leo interface + unified session contract.

No actual browser execution, login, or live data is tested here.
"""

import asyncio

import httpx

from src.gateway.app import create_app
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import StudentWebSessionStore


ISSUER = "https://issuer.example.invalid/"
ORIGIN = "https://chat.example.test"


class RejectingVerifier:
    async def verify_token(self, token):
        return None


def build_app(*, install=False):
    verifier = RejectingVerifier()

    app = create_app(
        token_verifier=verifier,
        student_lookup={},
        issuer=ISSUER,
        term_id="2027SP",
    )

    if install:
        async def unavailable_runner(**kwargs):
            raise RuntimeError("No live runner configured.")

        install_browser_session_routes(
            app,
            session_store=StudentWebSessionStore(
                student_lookup={},
                allowed_issuer=ISSUER,
            ),
            token_verifier=verifier,
            student_lookup={},
            allowed_issuer=ISSUER,
            session_origin=ORIGIN,
            term_id="2027SP",
            assistant_runner=unavailable_runner,
        )

    return app


def test_interactive_leo_page_is_opt_in():
    async def check():
        app = build_app(install=False)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=ORIGIN,
        ) as client:
            page = await client.get("/leo/session")
            assert page.status_code == 404

            preview = await client.get("/")
            assert preview.status_code == 200
            assert "una-lion-mark.png" in preview.text

    asyncio.run(check())


def test_leo_session_page_preserves_design_and_security():
    async def check():
        app = build_app(install=True)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=ORIGIN,
        ) as client:
            page = await client.get("/leo/session")

            assert page.status_code == 200
            assert page.headers["cache-control"] == "no-store"
            assert "Leo, your UNA planning assistant" in page.text
            assert 'src="/leo-assets/unified.js"' in page.text
            assert "una-lion-mark.png" in page.text

            assert "/auth/login" not in page.text
            assert 'id="send" type="submit" disabled' in page.text

            script = await client.get(
                "/leo-assets/unified.js"
            )
            assert script.status_code == 200
            assert "leo-team-plan-v1" in script.text
            assert 'JSON.stringify({ question: text })' in script.text
            assert '"X-CSRF-Token": csrfToken' in script.text
            assert "textContent" in script.text
            assert "innerHTML" not in script.text
            assert "localStorage" not in script.text
            assert "sessionStorage" not in script.text

            # A loaded UI must not grant academic access.
            anonymous = await client.get(
                "/api/student/session"
            )
            assert anonymous.status_code == 401

    asyncio.run(check())
