"""Leo static-asset exposure regression tests.

Original research HTML/JS remains in Git but cannot
be fetched from the default public asset endpoint.
"""

import asyncio

import httpx

from src.gateway.app import create_app
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import (
    StudentWebSessionStore,
)


ISSUER = "https://example.invalid/"
ORIGIN = "https://chat.example.test"


class RejectingVerifier:
    async def verify_token(self, token):
        return None


def make_app(*, sessions=False):
    verifier = RejectingVerifier()

    app = create_app(
        token_verifier=verifier,
        student_lookup={},
        issuer=ISSUER,
        term_id="2027SP",
    )

    if sessions:
        async def unavailable_runner(**kwargs):
            raise RuntimeError("Not configured.")

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


def test_public_preview_only_serves_approved_assets():
    async def check():
        app = make_app()

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=ORIGIN,
        ) as client:
            page = await client.get("/")
            assert page.status_code == 200
            assert "una-lion-mark.png" in page.text

            for name in (
                "styles.css",
                "interactive.css",
                "leo-theme.css",
                "unified.js",
                "una-lion-mark.png",
            ):
                result = await client.get(
                    f"/leo-assets/{name}"
                )
                assert result.status_code == 200, name

            for name in (
                "preview.html",
                "session.html",
                "interactive.html",
                "brand.js",
                "interactive.js",
                "leo-lion.svg",
                "unknown.js",
            ):
                result = await client.get(
                    f"/leo-assets/{name}"
                )
                assert result.status_code == 404, name

            assert (
                await client.get("/leo/session")
            ).status_code == 404

    asyncio.run(check())


def test_opt_in_session_page_still_requires_auth():
    async def check():
        app = make_app(sessions=True)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url=ORIGIN,
        ) as client:
            page = await client.get("/leo/session")
            assert page.status_code == 200
            assert 'src="/leo-assets/unified.js"' in (
                page.text
            )

            assert (
                await client.get(
                    "/leo-assets/session.html"
                )
            ).status_code == 404

            script = await client.get(
                "/leo-assets/unified.js"
            )
            assert script.status_code == 200

            # Serving the UI is not authentication.
            anonymous = await client.get(
                "/api/student/session"
            )
            assert anonymous.status_code == 401

    asyncio.run(check())
