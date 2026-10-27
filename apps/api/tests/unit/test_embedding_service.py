from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from api.services.embedding_service import EmbeddingService


@pytest.mark.asyncio
async def test_get_embedding_returns_1536_dim_vector():
    service = EmbeddingService(api_key="test-key")
    with patch.object(service, "_call_openai_embedding", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = [[0.01] * 1536]
        vec = await service.get_embedding("Answer Relevance formula")
        assert len(vec) == 1536
        assert isinstance(vec[0], float)


@pytest.mark.asyncio
async def test_get_embeddings_batch_handles_chunking():
    service = EmbeddingService(api_key="test-key")
    texts = ["text1", "text2", "text3"]
    with patch.object(service, "_call_openai_embedding", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = [[0.01] * 1536, [0.02] * 1536, [0.03] * 1536]
        results = await service.get_embeddings_batch(texts, batch_size=2)
        assert len(results) == 3
        assert len(results[0]) == 1536


@pytest.mark.asyncio
async def test_get_embeddings_batch_empty_list():
    service = EmbeddingService(api_key="test-key")
    results = await service.get_embeddings_batch([])
    assert results == []


@pytest.mark.asyncio
async def test_get_embedding_empty_string():
    service = EmbeddingService(api_key="test-key")
    with patch.object(service, "_call_openai_embedding", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = [[0.0] * 1536]
        vec = await service.get_embedding("   ")
        assert len(vec) == 1536
        # Confirm that stripped empty string gets sanitized before sending to OpenAI
        assert mock_api.called
        called_args = mock_api.call_args[0][0]
        assert called_args == [" "]


@pytest.mark.asyncio
async def test_service_initialization_api_key_fallback():
    with patch("api.services.embedding_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY.get_secret_value.return_value = "secret-key-123"
        mock_settings.OPENAI_BASE_URL = "https://api.openai.com/v1"
        service = EmbeddingService()
        assert service.api_key == "secret-key-123"


@pytest.mark.asyncio
async def test_service_initialization_missing_api_key():
    with patch("api.services.embedding_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = None
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            EmbeddingService()


@pytest.mark.asyncio
async def test_call_openai_embedding_httpx_success():
    service = EmbeddingService(api_key="sk-test")
    fake_response = {
        "object": "list",
        "data": [
            {"object": "embedding", "index": 1, "embedding": [0.2] * 1536},
            {"object": "embedding", "index": 0, "embedding": [0.1] * 1536},
        ],
        "model": "text-embedding-3-small",
        "usage": {"prompt_tokens": 10, "total_tokens": 10},
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_response
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await service._call_openai_embedding(["first", "second"])
        assert len(res) == 2
        # Verify ordering by index: index 0 should come first ([0.1]*1536)
        assert res[0][0] == 0.1
        assert res[1][0] == 0.2

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["model"] == "text-embedding-3-small"
        assert call_kwargs["json"]["input"] == ["first", "second"]
        assert call_kwargs["headers"]["Authorization"] == "Bearer sk-test"
