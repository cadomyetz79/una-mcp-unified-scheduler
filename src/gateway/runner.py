"""Trusted gateway -> authenticated MCP -> scheduling assistant.

The gateway resolves student identity before invoking this runner.
The MCP server independently verifies the forwarded bearer token.
No enrollment operations are exposed.
"""

import sys
from pathlib import Path
from typing import Any, Callable

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

# Existing team agent is a separate source directory.
# This fixed path is not derived from a browser request.
_AGENT_ROOT = Path(__file__).resolve().parents[2] / "ai-agent"
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

from agent.assistant import SchedulingAssistant
from agent.banner_tools import BannerTools

from src.mcp_server import team_security
from src.unified.plan_cards import project_verified_plan_cards


class AuthenticatedSchedulingRunner:
    """Execute one scheduling conversation with trusted identity."""

    def __init__(
        self,
        *,
        llm_factory: Callable[[], Any],
        transport: Any = None,
        policy_answerer: Any = None,
    ):
        if not callable(llm_factory):
            raise TypeError("An LLM factory is required.")

        self._llm_factory = llm_factory
        self._policy_answerer = policy_answerer

        # Optional ASGI transport is only for isolated integration tests.
        # Normal operation connects to the protected localhost MCP service.
        self._transport = transport

    async def __call__(
        self,
        *,
        question: str,
        student_id: str,
        term_id: str,
        bearer_token: str,
    ):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Invalid request.")

        if not isinstance(student_id, str) or not student_id:
            raise ValueError("Invalid student context.")

        if not isinstance(term_id, str) or not term_id:
            raise ValueError("Invalid term context.")

        if (
            not isinstance(bearer_token, str)
            or not bearer_token
            or len(bearer_token) > 16384
            or any(c.isspace() for c in bearer_token)
        ):
            raise ValueError("Invalid authentication context.")

        if question.lower().startswith("policy:"):
            if self._policy_answerer is None:
                raise PermissionError("Authorized policy retrieval is not configured.")
            return await self._policy_answerer(
                question=question.split(":", 1)[1].strip(),
                student_id=student_id, bearer_token=bearer_token,
            )

        # Canonical URL comes from trusted server configuration,
        # never from a request field or a model-generated tool argument.
        mcp_url = team_security.RESOURCE_URL

        async with httpx2.AsyncClient(
            transport=self._transport,
            base_url="http://127.0.0.1:8002",
            headers={
                "Authorization": f"Bearer {bearer_token}",
            },
            timeout=30.0,
        ) as http_client:

            async with Client(
                streamable_http_client(
                    mcp_url,
                    http_client=http_client,
                )
            ) as mcp_client:

                # Bound only to the identity already resolved by
                # the authenticated gateway.
                def project_cards(verified_plan):
                    return project_verified_plan_cards(
                        verified_plan,
                        expected_student_id=student_id,
                        expected_term_id=term_id,
                    )

                assistant = SchedulingAssistant(
                    BannerTools(mcp_client),
                    self._llm_factory(),
                    student_id,
                    term_id,
                    plan_card_projector=project_cards,
                )

                return await assistant.run(question)
