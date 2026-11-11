"""The old generic frontend is not publicly served."""

import asyncio
import httpx

from src.gateway.app import create_app
from src.mcp_server.team_security import RejectAllTokenVerifier


def test_legacy_ui_removed_without_affecting_leo():
    async def check():
        app = create_app(
            token_verifier=RejectAllTokenVerifier(),
            student_lookup={},
            issuer="https://example.invalid/",
            term_id="2027SP",
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://gateway.test",
        ) as client:
            for name in (
                "index.html",
                "styles.css",
                "app.js",
            ):
                result = await client.get(
                    f"/assets/{name}"
                )
                assert result.status_code == 404

            page = await client.get("/")
            assert page.status_code == 200
            assert "Leo, your UNA planning assistant" in page.text
            assert "una-lion-mark.png" in page.text

            lion = await client.get(
                "/leo-assets/una-lion-mark.png"
            )
            assert lion.status_code == 200

            denied = await client.post(
                "/api/chat",
                json={"question": "Plan CIS376"},
            )
            assert denied.status_code == 401

    asyncio.run(check())
