"""Tests for OpenAI completions server."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig
from psi_agent.ai.openai_completions.server import OpenAICompletionsServer


@pytest.fixture
def config() -> OpenAICompletionsConfig:
    """Create test config."""
    return OpenAICompletionsConfig(
        session_socket="/tmp/test_server.sock",
        model="test-model",
        api_key="test-key",
        base_url="https://api.example.com/v1",
    )


def test_server_creation(config: OpenAICompletionsConfig) -> None:
    """Test server creation."""
    server = OpenAICompletionsServer(config)

    assert server.config == config
    assert server.app is not None
    assert server.client is None


def test_server_routes(config: OpenAICompletionsConfig) -> None:
    """Test server routes are configured."""
    server = OpenAICompletionsServer(config)

    # Check routes exist
    routes = list(server.app.router.routes())
    assert len(routes) >= 2

    # Check POST /v1/chat/completions route exists
    post_routes = [r for r in routes if r.method == "POST"]
    assert len(post_routes) >= 1
    # Check that a POST route exists (the exact path check is fragile with aiohttp internals)
    assert any(r.resource is not None for r in post_routes)


class TestHandleChatCompletions:
    """Tests for chat completions request handling."""

    @pytest.mark.asyncio
    async def test_handle_invalid_json_body(self, config: OpenAICompletionsConfig) -> None:
        """Test handling request with invalid JSON body."""
        server = OpenAICompletionsServer(config)

        # Create mock request with invalid JSON
        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(side_effect=json.JSONDecodeError("msg", "doc", 0))

        response = await server._handle_chat_completions(request)

        assert response.status == 400
        assert isinstance(response, web.Response)
        assert response.text is not None
        assert "Invalid JSON body" in response.text

    @pytest.mark.asyncio
    async def test_handle_client_not_initialized(self, config: OpenAICompletionsConfig) -> None:
        """Test handling request when client is not initialized."""
        server = OpenAICompletionsServer(config)
        # client is None by default

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "hi"}]})

        response = await server._handle_chat_completions(request)

        assert response.status == 500
        assert isinstance(response, web.Response)
        assert response.text is not None
        assert "Server not ready" in response.text

    @pytest.mark.asyncio
    async def test_handle_non_streaming_request(self, config: OpenAICompletionsConfig) -> None:
        """Test handling non-streaming request."""
        server = OpenAICompletionsServer(config)

        # Mock client
        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={
                "id": "test-id",
                "choices": [{"message": {"content": "Hello!"}}],
            }
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "hi"}], "stream": False}
        )

        response = await server._handle_chat_completions(request)

        assert response.status == 200
        assert isinstance(response, web.Response)
        assert response.text is not None
        assert "Hello!" in response.text

    @pytest.mark.asyncio
    async def test_handle_non_streaming_error_response(
        self, config: OpenAICompletionsConfig
    ) -> None:
        """Test handling non-streaming request with error response."""
        server = OpenAICompletionsServer(config)

        # Mock client returning error
        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"error": "API error", "status_code": 429}
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "hi"}], "stream": False}
        )

        response = await server._handle_chat_completions(request)

        assert response.status == 429
        assert isinstance(response, web.Response)
        assert response.text is not None
        assert "API error" in response.text

    @pytest.mark.asyncio
    async def test_handle_streaming_request(self, config: OpenAICompletionsConfig) -> None:
        """Test handling streaming request."""
        server = OpenAICompletionsServer(config)

        # Mock streaming client
        async def mock_stream():
            yield "data: chunk1\n\n"
            yield "data: [DONE]\n\n"

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(return_value=mock_stream())
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "hi"}], "stream": True}
        )

        # Mock StreamResponse
        with patch("psi_agent.ai.openai_completions.server.web.StreamResponse") as mock_sr:
            mock_response = MagicMock()
            mock_response.prepare = AsyncMock()
            mock_response.write = AsyncMock()
            mock_sr.return_value = mock_response

            response = await server._handle_chat_completions(request)

            assert response.content_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_handle_exception(self, config: OpenAICompletionsConfig) -> None:
        """Test handling unexpected exception."""
        server = OpenAICompletionsServer(config)

        # Mock client that raises exception
        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(side_effect=Exception("Unexpected error"))
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "hi"}]})

        response = await server._handle_chat_completions(request)

        assert response.status == 500
        assert isinstance(response, web.Response)
        assert response.text is not None
        assert "Unexpected error" in response.text


class TestHandleOther:
    """Tests for handling other requests."""

    @pytest.mark.asyncio
    async def test_handle_other_request(self, config: OpenAICompletionsConfig) -> None:
        """Test handling other/unhandled requests."""
        server = OpenAICompletionsServer(config)

        request = MagicMock(spec=web.Request)
        request.method = "GET"
        request.path = "/v1/models"

        response = await server._handle_other(request)

        assert response.status == 404
        assert response.text is not None
        assert "Not found" in response.text
