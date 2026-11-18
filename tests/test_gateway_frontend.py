"""Browser frontend delivery and fail-closed preview contract."""

import asyncio

import httpx

from src.gateway.app import create_app
from src.mcp_server.team_security import RejectAllTokenVerifier


def test_frontend_and_same_origin_assets():
    api = create_app(
        token_verifier=RejectAllTokenVerifier(),
        student_lookup={},
        issuer="https://example.invalid/",
        term_id="2027SP",
    )

    async def check():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=api),
            base_url="http://gateway.test",
        ) as client:

            page = await client.get("/")
            assert page.status_code == 200
            assert "text/html" in page.headers["content-type"]
            assert page.headers["cache-control"] == "no-store"
            assert "frame-ancestors 'none'" in (
                page.headers["content-security-policy"]
            )
            assert "script-src 'self'" in (
                page.headers["content-security-policy"]
            )
            assert "Leo, your UNA planning assistant" in page.text
            assert "Preview only — sign-in not configured" in page.text
            assert 'href="/leo-assets/leo-theme.css"' in page.text
            assert 'src="/leo-assets/interactive.js"' not in page.text
            assert "/auth/login" not in page.text
            assert 'id="message"' in page.text
            assert 'id="send" type="submit" disabled' in page.text

            script = await client.get("/leo-assets/unified.js")
            stylesheet = await client.get("/leo-assets/leo-theme.css")
            lion = await client.get("/leo-assets/una-lion-mark.png")
            assert lion.status_code == 200
            assert lion.headers["content-type"].startswith("image/png")
            assert 'type="image/png" href="/leo-assets/una-lion-mark.png"' in page.text

            assert script.status_code == 200
            assert stylesheet.status_code == 200
            assert "text/javascript" in script.headers["content-type"]
            assert "text/css" in stylesheet.headers["content-type"]

            # Browser must treat answers as plain text, not HTML.
            assert "textContent" in script.text
            assert "innerHTML" not in script.text
            assert "document.write" not in script.text

            # No browser credential persistence or embedded bearer tokens.
            assert "localStorage" not in script.text
            assert "sessionStorage" not in script.text
            assert "Authorization" not in script.text
            assert "Bearer " not in script.text

            # A served UI is not an authentication bypass.
            denied = await client.post(
                "/api/chat",
                json={"question": "Plan CIS376 and CIS410"},
            )
            assert denied.status_code == 401
            assert denied.headers["cache-control"] == "no-store"

    asyncio.run(check())
