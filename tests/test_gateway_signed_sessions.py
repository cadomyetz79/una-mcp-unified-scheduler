"""Signed synthetic JWT -> browser session -> unified gateway tests.

No real Microsoft credentials, Entra calls, OAuth login, or
production identity records are used.
"""

import asyncio
import time
from types import SimpleNamespace

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from src.gateway.app import create_app
from src.gateway.session_routes import (
    install_browser_session_routes,
)
from src.gateway.web_sessions import (
    SESSION_COOKIE_NAME,
    StudentWebSessionStore,
)
from src.mcp_server.entra_token_verifier import (
    EntraTokenVerifier,
)


TENANT = "11111111-1111-4111-8111-111111111111"
AUDIENCE = "22222222-2222-4222-8222-222222222222"
CLIENT = "33333333-3333-4333-8333-333333333333"
OID_A = "44444444-4444-4444-8444-444444444444"
OID_B = "55555555-5555-4555-8555-555555555555"

ISSUER = f"https://login.microsoftonline.com/{TENANT}/v2.0"
ORIGIN = "https://chat.example.test"

LOOKUP = {
    (TENANT, OID_A): "S10001",
    (TENANT, OID_B): "S10002",
}


@pytest.fixture
def environment(monkeypatch):
    signing_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = {"value": signing_key.public_key()}

    verifier = EntraTokenVerifier(
        tenant_id=TENANT,
        audience=AUDIENCE,
    )

    monkeypatch.setattr(
        verifier._jwks_client,
        "get_signing_key_from_jwt",
        lambda raw: SimpleNamespace(key=public_key["value"]),
    )

    store = StudentWebSessionStore(
        student_lookup=LOOKUP,
        allowed_issuer=ISSUER,
    )

    calls = []
    wrong_card_identity = {"enabled": False}

    async def runner(**kwargs):
        calls.append(kwargs)

        student_id = (
            "S10002"
            if wrong_card_identity["enabled"]
            else kwargs["student_id"]
        )

        return SimpleNamespace(
            answer="Verified synthetic schedule proposal.",
            plan_cards={
                "schema_version": "leo-team-plan-v1",
                "status": "proposed_only",
                "student_id": student_id,
                "term_id": "2027SP",
                "options": [],
            },
            stopped_reason="answered",
            grounded=True,
            trace={"secret": "never exposed"},
        )

    app = create_app(
        token_verifier=verifier,
        student_lookup=LOOKUP,
        issuer=ISSUER,
        term_id="2027SP",
    )

    install_browser_session_routes(
        app,
        session_store=store,
        token_verifier=verifier,
        student_lookup=LOOKUP,
        allowed_issuer=ISSUER,
        session_origin=ORIGIN,
        term_id="2027SP",
        assistant_runner=runner,
    )

    def sign(oid=OID_A, **overrides):
        now = int(time.time())

        claims = {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "tid": TENANT,
            "oid": oid,
            "azp": CLIENT,
            "scp": "academic.read",
            "ver": "2.0",
            "iat": now,
            "nbf": now,
            "exp": now + 600,
        }

        claims.update(overrides)

        return jwt.encode(
            claims,
            signing_key,
            algorithm="RS256",
            headers={"kid": "local-research-test-key"},
        )

    async def issue(oid=OID_A):
        raw = sign(oid)
        verified = await verifier.verify_token(raw)

        assert verified is not None

        ticket = store.issue(
            verified_access_token=verified
        )

        return ticket, raw

    return SimpleNamespace(
        app=app,
        verifier=verifier,
        store=store,
        sign=sign,
        issue=issue,
        calls=calls,
        public_key=public_key,
        wrong_card_identity=wrong_card_identity,
    )


def test_two_signed_students_remain_isolated(environment):
    async def check():
        env = environment

        for oid, expected in (
            (OID_A, "S10001"),
            (OID_B, "S10002"),
        ):
            ticket, raw_token = await env.issue(oid)

            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=env.app),
                base_url=ORIGIN,
                cookies={
                    SESSION_COOKIE_NAME: ticket.cookie_value
                },
            ) as client:
                status = await client.get(
                    "/api/student/session"
                )

                assert status.status_code == 200
                assert status.json()["student_id"] == expected

                csrf = status.json()["csrf_token"]

                result = await client.post(
                    "/api/student/session/chat",
                    headers={
                        "Origin": ORIGIN,
                        "X-CSRF-Token": csrf,
                    },
                    json={
                        "question": "Plan my Spring 2027 classes"
                    },
                )

                assert result.status_code == 200
                assert result.json()["plan_cards"][
                    "student_id"
                ] == expected

                assert raw_token not in result.text
                assert ticket.cookie_value not in result.text
                assert csrf not in result.text
                assert "trace" not in result.json()

        assert [
            call["student_id"] for call in env.calls
        ] == ["S10001", "S10002"]

        assert all(
            call["term_id"] == "2027SP"
            for call in env.calls
        )

    asyncio.run(check())


def test_invalid_signed_identity_cannot_issue_session(environment):
    async def check():
        env = environment

        invalid = [
            env.sign(aud="wrong-audience"),
            env.sign(scp="not.academic.read"),
            env.sign(oid="not-an-authorized-student"),
        ]

        forged_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Valid-looking claims, invalid signing key.
        claims = jwt.decode(
            env.sign(),
            options={"verify_signature": False},
        )

        invalid.append(
            jwt.encode(
                claims,
                forged_key,
                algorithm="RS256",
                headers={"kid": "forged-key"},
            )
        )

        for raw in invalid:
            try:
                verified = await env.verifier.verify_token(raw)
            except Exception:
                verified = None

            if verified is None:
                continue

            with pytest.raises(PermissionError):
                env.store.issue(
                    verified_access_token=verified
                )

        assert env.store.count() == 0
        assert env.calls == []

    asyncio.run(check())


def test_revoked_signature_and_wrong_student_cards(environment):
    async def check():
        env = environment
        ticket, _ = await env.issue(OID_A)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=env.app),
            base_url=ORIGIN,
            cookies={
                SESSION_COOKIE_NAME: ticket.cookie_value
            },
        ) as client:
            status = await client.get(
                "/api/student/session"
            )

            assert status.status_code == 200
            csrf = status.json()["csrf_token"]

            env.wrong_card_identity["enabled"] = True

            result = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf,
                },
                json={"question": "Plan my schedule"},
            )

            assert result.status_code == 200

            # Model-side or stale cross-student cards must
            # never be returned to the browser.
            assert result.json()["plan_cards"] is None

            assert len(env.calls) == 1

            # Simulate a signing key that is no longer trusted.
            env.public_key["value"] = (
                rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                ).public_key()
            )

            rejected = await client.get(
                "/api/student/session"
            )

            assert rejected.status_code == 401

            denied_chat = await client.post(
                "/api/student/session/chat",
                headers={
                    "Origin": ORIGIN,
                    "X-CSRF-Token": csrf,
                },
                json={"question": "Plan my schedule"},
            )

            assert denied_chat.status_code == 401
            assert len(env.calls) == 1

    asyncio.run(check())
