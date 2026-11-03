"""Read-only RAGFlow retrieval adapter.

Only approved public/synthetic datasets should be configured.
No real UNA student data belongs in this retrieval path.
"""

import re
from urllib.parse import urlsplit

import httpx2

from src.agent.knowledge_retrieval import KnowledgeHit


class RAGFlowRetriever:
    """Convert RAGFlow's HTTP retrieval results to KnowledgeHit."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        dataset_ids: list[str] | tuple[str, ...],
        client: httpx2.AsyncClient | None = None,
    ):
        parsed = urlsplit(base_url)

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.path not in {"", "/"}
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Invalid RAGFlow server URL.")

        if (
            parsed.scheme == "http"
            and parsed.hostname not in {
                "localhost", "127.0.0.1", "::1"
            }
        ):
            raise ValueError(
                "Non-local RAGFlow requires HTTPS."
            )

        if (
            not isinstance(api_key, str)
            or not api_key
            or any(c.isspace() for c in api_key)
        ):
            raise ValueError("Invalid RAGFlow API key.")

        if (
            not isinstance(dataset_ids, (tuple, list))
            or not dataset_ids
            or any(
                not isinstance(item, str)
                or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", item)
                is None
                for item in dataset_ids
            )
        ):
            raise ValueError("Invalid RAGFlow dataset configuration.")

        if len(set(dataset_ids)) != len(dataset_ids):
            raise ValueError("Duplicate RAGFlow dataset IDs.")

        self.endpoint = base_url.rstrip("/") + "/api/v1/retrieval"
        self.api_key = api_key
        self.dataset_ids = tuple(dataset_ids)
        self.client = client

    async def search(
        self,
        query: str,
        limit: int,
    ) -> list[KnowledgeHit]:
        if (
            not isinstance(query, str)
            or not query.strip()
            or len(query) > 500
            or any(ord(c) < 32 for c in query)
            or type(limit) is not int
            or not 1 <= limit <= 5
        ):
            raise ValueError("Invalid RAGFlow retrieval request.")

        if self.client is not None:
            return await self._retrieve(self.client, query, limit)

        async with httpx2.AsyncClient(
            timeout=10.0,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            return await self._retrieve(client, query, limit)

    async def _retrieve(self, client, query, limit):
        try:
            response = await client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "question": query.strip(),
                    "dataset_ids": list(self.dataset_ids),
                    "page": 1,
                    "page_size": limit,
                },
            )
        except httpx2.HTTPError:
            raise RuntimeError(
                "RAGFlow retrieval transport failed."
            ) from None

        if response.status_code != 200:
            raise RuntimeError(
                "RAGFlow retrieval HTTP request failed."
            )

        if len(response.content) > 1_000_000:
            raise ValueError("RAGFlow response exceeds size limit.")

        try:
            payload = response.json()
        except ValueError:
            raise ValueError(
                "RAGFlow returned invalid JSON."
            ) from None

        if (
            not isinstance(payload, dict)
            or type(payload.get("code")) is not int
            or payload["code"] != 0
            or not isinstance(payload.get("data"), dict)
            or not isinstance(
                payload["data"].get("chunks"), list
            )
        ):
            raise ValueError("RAGFlow retrieval response rejected.")

        hits = []

        for chunk in payload["data"]["chunks"][:limit]:
            if not isinstance(chunk, dict):
                raise ValueError("Invalid RAGFlow chunk.")

            dataset_id = chunk.get("dataset_id")
            document_id = chunk.get("document_id")
            chunk_id = chunk.get("id")
            title = (
                chunk.get("document_keyword")
                or chunk.get("docnm_kwd")
            )
            content = chunk.get("content")

            if (
                dataset_id not in self.dataset_ids
                or any(
                    not isinstance(value, str)
                    or not value.strip()
                    for value in (
                        document_id, chunk_id, title, content
                    )
                )
            ):
                raise ValueError(
                    "RAGFlow chunk lacks trusted source metadata."
                )

            hits.append(
                KnowledgeHit(
                    source_id=(
                        f"{dataset_id}/{document_id}/{chunk_id}"
                    ),
                    title=title.strip()[:200],
                    excerpt=content.strip()[:1200],
                )
            )

        return hits
