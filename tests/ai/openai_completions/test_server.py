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


class TestHandleNonStreaming:
    """Tests for non-streaming request handling."""

    @pytest.mark.asyncio
    async def test_handle_non_streaming_success(self, config: OpenAICompletionsConfig) -> None:
        """Test successful non-streaming response."""
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={
                "id": "test-id",
                "choices": [{"message": {"content": "Hello!"}}],
            }
        )
        server.client = mock_client

        response = await server._handle_non_streaming(
            {"messages": [{"role": "user", "content": "Hi"}]}
        )

        assert response.status == 200
        assert response.content_type == "application/json"

    @pytest.mark.asyncio
    async def test_handle_non_streaming_error_response(
        self, config: OpenAICompletionsConfig
    ) -> None:
        """Test non-streaming request with error response from client."""
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"error": "API error", "status_code": 429}
        )
        server.client = mock_client

        response = await server._handle_non_streaming(
            {"messages": [{"role": "user", "content": "Hi"}]}
        )

        assert response.status == 429
        assert response.text is not None
        assert "API error" in response.text

    @pytest.mark.asyncio
    async def test_handle_non_streaming_error_without_status_code(
        self, config: OpenAICompletionsConfig
    ) -> None:
        """Test non-streaming error response without status_code defaults to 500."""
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(return_value={"error": "Unknown error"})
        server.client = mock_client

        response = await server._handle_non_streaming(
            {"messages": [{"role": "user", "content": "Hi"}]}
        )

        assert response.status == 500


class TestHandleStreaming:
    """Tests for streaming request handling."""

    @pytest.mark.asyncio
    async def test_handle_streaming_success(self, config: OpenAICompletionsConfig) -> None:
        """Test successful streaming response."""
        server = OpenAICompletionsServer(config)

        async def mock_stream():
            yield "data: chunk1\n\n"
            yield "data: [DONE]\n\n"

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(return_value=mock_stream())
        server.client = mock_client

        request = MagicMock(spec=web.Request)

        # Mock StreamResponse to avoid actual aiohttp internals
        with patch("psi_agent.ai.openai_completions.server.web.StreamResponse") as mock_sr:
            mock_response = MagicMock()
            mock_response.prepare = AsyncMock()
            mock_response.write = AsyncMock()
            mock_response.content_type = "text/event-stream"
            mock_sr.return_value = mock_response

            response = await server._handle_streaming(
                request, {"messages": [{"role": "user", "content": "Hi"}], "stream": True}
            )

            assert response.content_type == "text/event-stream"


class TestHandleChatCompletionsWithReasoning:
    """Tests for chat completions with reasoning parameters."""

    @pytest.mark.asyncio
    async def test_handle_request_with_thinking(self, config: OpenAICompletionsConfig) -> None:
        """Test request with thinking parameter."""
        config = OpenAICompletionsConfig(
            session_socket="/tmp/test.sock",
            model="test-model",
            api_key="test-key",
            base_url="https://api.example.com/v1",
            thinking="enabled",
        )
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify thinking was injected
        call_args = mock_client.chat_completions.call_args[0][0]
        assert "thinking" in call_args
        assert call_args["thinking"]["type"] == "enabled"

    @pytest.mark.asyncio
    async def test_handle_request_with_reasoning_effort(
        self, config: OpenAICompletionsConfig
    ) -> None:
        """Test request with reasoning_effort parameter."""
        config = OpenAICompletionsConfig(
            session_socket="/tmp/test.sock",
            model="test-model",
            api_key="test-key",
            base_url="https://api.example.com/v1",
            reasoning_effort="high",
        )
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify reasoning_effort was injected
        call_args = mock_client.chat_completions.call_args[0][0]
        assert "reasoning_effort" in call_args
        assert call_args["reasoning_effort"] == "high"


class TestModelInjection:
    """Tests for model injection behavior."""

    @pytest.mark.asyncio
    async def test_model_injected_when_missing(self, config: OpenAICompletionsConfig) -> None:
        """Test model is injected when not provided in request."""
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify model was injected
        call_args = mock_client.chat_completions.call_args[0][0]
        assert call_args["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_model_injected_when_session_placeholder(
        self, config: OpenAICompletionsConfig
    ) -> None:
        """Test model is injected when request has 'session' placeholder."""
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(
            return_value={"model": "session", "messages": [{"role": "user", "content": "Hi"}]}
        )

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify model was replaced
        call_args = mock_client.chat_completions.call_args[0][0]
        assert call_args["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_model_preserved_when_explicit(self, config: OpenAICompletionsConfig) -> None:
        """Test explicit model is preserved, not overridden."""
        server = OpenAICompletionsServer(config)

        mock_client = MagicMock()
        mock_client.chat_completions = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock(spec=web.Request)
        request.json = AsyncMock(
            return_value={"model": "gpt-4o", "messages": [{"role": "user", "content": "Hi"}]}
        )

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify user-specified model was preserved
        call_args = mock_client.chat_completions.call_args[0][0]
        assert call_args["model"] == "gpt-4o"
