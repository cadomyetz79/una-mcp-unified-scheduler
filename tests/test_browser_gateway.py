"""Gateway boundary tests using synthetic verified-token fixtures.

The fake verifier is injected only into isolated test application instances.
Cryptographic JWT verification is covered by the existing verifier tests.
"""

import asyncio
from types import SimpleNamespace

import httpx
from mcp.server.auth.provider import AccessToken

from src.gateway.app import create_app


ISSUER = "https://test-issuer.example.invalid/"
TENANT = "11111111-1111-4111-8111-111111111111"
USER_A = "44444444-4444-4444-8444-444444444444"
USER_B = "55555555-5555-4555-8555-555555555555"


class SyntheticVerifier:
    async def verify_token(self, token):
        if token not in ("valid-a", "valid-b"):
            return None

        user = USER_A if token == "valid-a" else USER_B

        return AccessToken(
            token=token,
            client_id="synthetic-test-client",
            scopes=["academic.read"],
            expires_at=9999999999,
            resource="synthetic-test-resource",
            subject=f"{TENANT}:{user}",
            claims={
                "iss": ISSUER,
                "tid": TENANT,
                "oid": user,
            },
        )


def gateway(runner=None, mappings=None):
    if mappings is None:
        mappings = {(TENANT, USER_A): "S10001"}

    return create_app(
        token_verifier=SyntheticVerifier(),
        student_lookup=mappings,
        issuer=ISSUER,
        term_id="2027SP",
        assistant_runner=runner,
    )


async def request(app, token=None, body=None):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://gateway.test",
    ) as client:
        return await client.post(
            "/api/chat",
            json=body or {"question": "Plan CIS376 and CIS410"},
            headers=headers,
        )


def test_anonymous_request_rejected():
    response = asyncio.run(request(gateway()))
    assert response.status_code == 401


def test_invalid_token_rejected():
    response = asyncio.run(request(gateway(), "forged"))
    assert response.status_code == 401


def test_unmapped_student_rejected():
    response = asyncio.run(request(gateway(), "valid-b"))
    assert response.status_code == 403


def test_valid_identity_without_runner_fails_closed():
    response = asyncio.run(request(gateway(), "valid-a"))
    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Scheduling service is not configured."
    )


def test_browser_cannot_supply_student_identity():
    called = []

    async def runner(**kwargs):
        called.append(kwargs)
        return SimpleNamespace(
            answer="No enrollment performed.",
            plan_cards=None,
            stopped_reason="answered",
            grounded=True,
        )

    response = asyncio.run(request(
        gateway(runner),
        "valid-a",
        {
            "question": "Plan CIS376",
            "student_id": "S10002",
        },
    ))

    assert response.status_code == 422
    assert called == []


def test_authorized_request_uses_server_identity():
    observed = []

    async def runner(**kwargs):
        observed.append(kwargs)
        return SimpleNamespace(
            answer="Proposed only; no enrollment performed.",
            plan_cards=None,
            stopped_reason="answered",
            grounded=True,
            security={"private": "do not expose"},
            mcp_calls=[{"private": "do not expose"}],
        )

    response = asyncio.run(request(
        gateway(runner),
        "valid-a",
    ))

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Proposed only; no enrollment performed.",
        "plan_cards": None,
    }
    assert observed[0]["student_id"] == "S10001"
    assert observed[0]["term_id"] == "2027SP"
    assert observed[0]["bearer_token"] == "valid-a"
    assert response.headers["cache-control"] == "no-store"
    assert "private" not in response.text
    assert "valid-a" not in response.text


def test_cross_student_cards_are_suppressed():
    async def runner(**kwargs):
        return SimpleNamespace(
            answer="A synthetic schedule was checked.",
            stopped_reason="answered",
            grounded=True,
            plan_cards={
                "status": "proposed_only",
                "student_id": "S10002",
                "term_id": "2027SP",
                "options": [],
            },
        )

    response = asyncio.run(request(gateway(runner), "valid-a"))
    assert response.status_code == 200
    assert response.json()["plan_cards"] is None


def test_runner_exception_is_not_exposed():
    async def runner(**kwargs):
        raise RuntimeError("Secret internal service failure")

    response = asyncio.run(request(gateway(runner), "valid-a"))

    assert response.status_code == 503
    assert "Secret internal" not in response.text
