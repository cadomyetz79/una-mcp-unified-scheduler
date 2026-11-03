"""RAGFlow adapter tests; no network or credentials."""

import asyncio
import json

import httpx2
import pytest

from src.agent.knowledge_retrieval import retrieve_public_knowledge
from src.agent.ragflow_adapter import RAGFlowRetriever


DATASET = "synthetic_dataset_001"
CHUNK = {
    "id": "chunk001",
    "dataset_id": DATASET,
    "document_id": "document001",
    "document_keyword": "Synthetic Registration Guide",
    "content": "Synthetic registration guidance for tests.",
}


def make_retriever(handler):
    client = httpx2.AsyncClient(
        transport=httpx2.MockTransport(handler),
        trust_env=False,
    )

    retriever = RAGFlowRetriever(
        base_url="http://127.0.0.1:9380",
        api_key="synthetic-test-key",
        dataset_ids=[DATASET],
        client=client,
    )

    return retriever, client


def test_successful_retrieval():
    def handler(request):
        assert request.method == "POST"
        assert request.url.path == "/api/v1/retrieval"
        assert request.headers["authorization"] == (
            "Bearer synthetic-test-key"
        )

        body = json.loads(request.content)
        assert body["dataset_ids"] == [DATASET]
        assert body["question"] == "registration?"
        assert body["page_size"] == 3

        return httpx2.Response(
            200,
            json={"code": 0, "data": {"chunks": [CHUNK]}},
        )

    async def check():
        retriever, client = make_retriever(handler)

        async with client:
            results = await retrieve_public_knowledge(
                retriever, "registration?"
            )

        assert len(results) == 1
        assert results[0].title == "Synthetic Registration Guide"
        assert results[0].source_id == (
            f"{DATASET}/document001/chunk001"
        )

    asyncio.run(check())


def test_empty_results():
    def handler(request):
        return httpx2.Response(
            200,
            json={"code": 0, "data": {"chunks": []}},
        )

    async def check():
        retriever, client = make_retriever(handler)
        async with client:
            assert await retrieve_public_knowledge(
                retriever, "registration"
            ) == []

    asyncio.run(check())


@pytest.mark.parametrize(
    "response",
    [
        {"code": 102, "message": "retrieval failed"},
        {"code": 0, "data": {}},
        {
            "code": 0,
            "data": {
                "chunks": [
                    {**CHUNK, "dataset_id": "other_dataset"}
                ]
            },
        },
        {
            "code": 0,
            "data": {
                "chunks": [
                    {**CHUNK, "document_id": ""}
                ]
            },
        },
    ],
)
def test_invalid_responses_rejected(response):
    def handler(request):
        return httpx2.Response(200, json=response)

    async def check():
        retriever, client = make_retriever(handler)
        async with client:
            with pytest.raises(ValueError):
                await retrieve_public_knowledge(
                    retriever, "registration"
                )

    asyncio.run(check())


def test_http_auth_failure_does_not_leak_key():
    def handler(request):
        return httpx2.Response(
            401,
            json={"message": "synthetic-test-key"},
        )

    async def check():
        retriever, client = make_retriever(handler)
        async with client:
            with pytest.raises(RuntimeError) as caught:
                await retrieve_public_knowledge(
                    retriever, "registration"
                )

        assert "synthetic-test-key" not in str(caught.value)

    asyncio.run(check())


def test_nonlocal_http_rejected():
    with pytest.raises(ValueError):
        RAGFlowRetriever(
            base_url="http://ragflow.example.com",
            api_key="synthetic-test-key",
            dataset_ids=[DATASET],
        )
