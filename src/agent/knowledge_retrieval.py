"""Contract for public institutional knowledge retrieval.

The RAG implementation remains a separate component.
Retrieved documents are evidence, not trusted instructions.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class KnowledgeHit:
    """One source-backed institutional knowledge result."""

    source_id: str
    title: str
    excerpt: str
    section: str | None = None


class PublicKnowledgeRetriever(Protocol):
    """Interface implemented by a future RAG adapter."""

    async def search(
        self,
        query: str,
        limit: int,
    ) -> list[KnowledgeHit]:
        ...


async def retrieve_public_knowledge(
    retriever: PublicKnowledgeRetriever,
    query: str,
    limit: int = 3,
) -> list[KnowledgeHit]:
    """Validate a public-knowledge retrieval request and results."""

    if not isinstance(query, str):
        raise ValueError("Knowledge query must be text.")

    cleaned = query.strip()

    if (
        not cleaned
        or len(cleaned) > 500
        or any(ord(char) < 32 for char in cleaned)
    ):
        raise ValueError("Invalid knowledge query.")

    if not isinstance(limit, int) or not 1 <= limit <= 5:
        raise ValueError("Knowledge result limit must be 1–5.")

    results = await retriever.search(cleaned, limit)

    if not isinstance(results, list) or len(results) > limit:
        raise ValueError("Invalid knowledge retrieval results.")

    for result in results:
        if not isinstance(result, KnowledgeHit):
            raise ValueError("Invalid knowledge result type.")

        required = (
            result.source_id,
            result.title,
            result.excerpt,
        )

        if any(
            not isinstance(value, str) or not value.strip()
            for value in required
        ):
            raise ValueError("Knowledge result missing source data.")

        if len(result.excerpt) > 1200:
            raise ValueError("Knowledge excerpt exceeds limit.")

    return results
