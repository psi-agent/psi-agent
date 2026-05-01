"""Tests for Anthropic Messages server."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig
from psi_agent.ai.anthropic_messages.server import AnthropicMessagesServer


@pytest.fixture
def config() -> AnthropicMessagesConfig:
    """Create test config."""
    return AnthropicMessagesConfig(
        session_socket="/tmp/test_server.sock",
        model="claude-sonnet-4-20250514",
        api_key="test-key",
    )


@pytest.fixture
def server(config: AnthropicMessagesConfig) -> AnthropicMessagesServer:
    """Create test server."""
    return AnthropicMessagesServer(config)


class TestAnthropicMessagesServer:
    """Tests for AnthropicMessagesServer."""

    def test_server_creation(
        self, server: AnthropicMessagesServer, config: AnthropicMessagesConfig
    ) -> None:
        """Test server creation."""
        assert server.config == config
        assert server.client is None
        assert server._runner is None

    def test_routes_configured(self, server: AnthropicMessagesServer) -> None:
        """Test that routes are configured."""
        routes = [r.resource.canonical for r in server.app.router.routes() if r.resource]
        assert "/v1/chat/completions" in routes

    @pytest.mark.asyncio
    async def test_handle_chat_completions_invalid_json(
        self, server: AnthropicMessagesServer
    ) -> None:
        """Test handling invalid JSON request."""
        request = MagicMock()
        request.json = AsyncMock(side_effect=Exception("Invalid JSON"))

        # Patch json.JSONDecodeError handling
        request.json = AsyncMock(side_effect=json.JSONDecodeError("test", "test", 0))

        response = await server._handle_chat_completions(request)
        assert response.status == 400

    @pytest.mark.asyncio
    async def test_handle_chat_completions_client_not_initialized(
        self, server: AnthropicMessagesServer
    ) -> None:
        """Test handling request when client not initialized."""
        request = MagicMock()
        request.json = AsyncMock(return_value={"messages": []})

        response = await server._handle_chat_completions(request)
        assert response.status == 500

    @pytest.mark.asyncio
    async def test_handle_other_request(self, server: AnthropicMessagesServer) -> None:
        """Test handling unhandled request path."""
        request = MagicMock()
        request.method = "GET"
        request.path = "/v1/unknown"

        response = await server._handle_other(request)
        assert response.status == 404

    @pytest.mark.asyncio
    async def test_start_creates_socket(self, config: AnthropicMessagesConfig) -> None:
        """Test that start creates socket file."""

        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = os.path.join(tmpdir, "test.sock")
            config = AnthropicMessagesConfig(
                session_socket=str(socket_path),
                model="claude-sonnet-4-20250514",
                api_key="test-key",
            )
            server = AnthropicMessagesServer(config)

            # Mock the client to avoid actual API calls
            # Mock UnixSite to avoid actual socket binding
            with (
                patch.object(server, "client", None),
                patch("aiohttp.web.UnixSite") as mock_unix_site,
            ):
                mock_site = AsyncMock()
                mock_unix_site.return_value = mock_site

                await server.start()

                # Check client was initialized
                assert server.client is not None
                assert server._runner is not None

                await server.stop()

    @pytest.mark.asyncio
    async def test_stop_cleans_up(self, server: AnthropicMessagesServer) -> None:
        """Test that stop cleans up resources."""
        # Setup mocks
        server.client = AsyncMock()
        server.client.__aexit__ = AsyncMock()
        server._runner = AsyncMock()
        server._runner.cleanup = AsyncMock()

        await server.stop()

        server.client.__aexit__.assert_called_once()
        server._runner.cleanup.assert_called_once()


class TestHandleNonStreaming:
    """Tests for non-streaming request handling."""

    @pytest.fixture
    def server_with_client(self, config: AnthropicMessagesConfig) -> AnthropicMessagesServer:
        """Create server with mocked client."""
        server = AnthropicMessagesServer(config)
        server.client = AsyncMock()
        return server

    @pytest.mark.asyncio
    async def test_handle_non_streaming_success(
        self, server_with_client: AnthropicMessagesServer
    ) -> None:
        """Test successful non-streaming response."""
        mock_client = server_with_client.client
        assert mock_client is not None
        # Use cast to avoid type errors when mocking
        cast(Any, mock_client).messages = AsyncMock(
            return_value={
                "id": "test-id",
                "choices": [{"message": {"content": "Hello!"}}],
            }
        )

        response = await server_with_client._handle_non_streaming(
            {"messages": [{"role": "user", "content": "Hi"}]}
        )

        assert response.status == 200
        assert response.content_type == "application/json"

    @pytest.mark.asyncio
    async def test_handle_non_streaming_error_response(
        self, server_with_client: AnthropicMessagesServer
    ) -> None:
        """Test non-streaming request with error response from client."""
        mock_client = server_with_client.client
        assert mock_client is not None
        cast(Any, mock_client).messages = AsyncMock(
            return_value={"error": "API error", "status_code": 429}
        )

        response = await server_with_client._handle_non_streaming(
            {"messages": [{"role": "user", "content": "Hi"}]}
        )

        assert response.status == 429
        assert response.text is not None
        assert "API error" in response.text

    @pytest.mark.asyncio
    async def test_handle_non_streaming_error_without_status_code(
        self, server_with_client: AnthropicMessagesServer
    ) -> None:
        """Test non-streaming error response without status_code defaults to 500."""
        mock_client = server_with_client.client
        assert mock_client is not None
        cast(Any, mock_client).messages = AsyncMock(return_value={"error": "Unknown error"})

        response = await server_with_client._handle_non_streaming(
            {"messages": [{"role": "user", "content": "Hi"}]}
        )

        assert response.status == 500


class TestHandleStreaming:
    """Tests for streaming request handling."""

    @pytest.fixture
    def server_with_client(self, config: AnthropicMessagesConfig) -> AnthropicMessagesServer:
        """Create server with mocked client."""
        server = AnthropicMessagesServer(config)
        server.client = AsyncMock()
        return server

    @pytest.mark.asyncio
    async def test_handle_streaming_success(
        self, server_with_client: AnthropicMessagesServer
    ) -> None:
        """Test successful streaming response."""

        async def mock_stream():
            yield "data: chunk1\n\n"
            yield "data: [DONE]\n\n"

        mock_client = server_with_client.client
        assert mock_client is not None
        cast(Any, mock_client).messages = AsyncMock(return_value=mock_stream())

        # Mock StreamResponse to avoid actual aiohttp internals
        with patch("psi_agent.ai.anthropic_messages.server.web.StreamResponse") as mock_sr:
            mock_response = MagicMock()
            mock_response.prepare = AsyncMock()
            mock_response.write = AsyncMock()
            mock_response.content_type = "text/event-stream"
            mock_sr.return_value = mock_response

            request = MagicMock()
            response = await server_with_client._handle_streaming(
                request, {"messages": [{"role": "user", "content": "Hi"}], "stream": True}
            )

            assert response.content_type == "text/event-stream"


class TestHandleChatCompletionsWithReasoning:
    """Tests for chat completions with reasoning parameters."""

    @pytest.mark.asyncio
    async def test_handle_request_with_thinking(self, config: AnthropicMessagesConfig) -> None:
        """Test request with thinking parameter."""
        config = AnthropicMessagesConfig(
            session_socket="/tmp/test.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
            thinking="enabled",
        )
        server = AnthropicMessagesServer(config)

        # Mock client
        mock_client = AsyncMock()
        cast(Any, mock_client).messages = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock()
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify thinking was injected
        call_args = mock_client.messages.call_args[0][0]
        assert "thinking" in call_args
        assert call_args["thinking"]["type"] == "enabled"

    @pytest.mark.asyncio
    async def test_handle_request_with_reasoning_effort(
        self, config: AnthropicMessagesConfig
    ) -> None:
        """Test request with reasoning_effort parameter."""
        config = AnthropicMessagesConfig(
            session_socket="/tmp/test.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
            reasoning_effort="high",
        )
        server = AnthropicMessagesServer(config)

        # Mock client
        mock_client = AsyncMock()
        cast(Any, mock_client).messages = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock()
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify reasoning_effort was injected
        call_args = mock_client.messages.call_args[0][0]
        assert "output_config" in call_args
        assert call_args["output_config"]["effort"] == "high"

    @pytest.mark.asyncio
    async def test_handle_request_exception(self, server: AnthropicMessagesServer) -> None:
        """Test handling exception during request processing."""
        # Mock client that raises exception
        mock_client = AsyncMock()
        cast(Any, mock_client).messages = AsyncMock(side_effect=Exception("Unexpected error"))
        server.client = mock_client

        request = MagicMock()
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 500
        # Response is web.Response, not StreamResponse for error cases
        from aiohttp import web

        assert isinstance(response, web.Response)
        assert response.text is not None
        assert "Unexpected error" in response.text


class TestModelInjection:
    """Tests for model injection behavior."""

    @pytest.mark.asyncio
    async def test_model_injected_when_missing(self, config: AnthropicMessagesConfig) -> None:
        """Test model is injected when not provided in request."""
        server = AnthropicMessagesServer(config)

        mock_client = AsyncMock()
        cast(Any, mock_client).messages = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock()
        request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "Hi"}]})

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify model was injected
        call_args = mock_client.messages.call_args[0][0]
        assert call_args["model"] == "claude-sonnet-4-20250514"

    @pytest.mark.asyncio
    async def test_model_injected_when_session_placeholder(
        self, config: AnthropicMessagesConfig
    ) -> None:
        """Test model is injected when request has 'session' placeholder."""
        server = AnthropicMessagesServer(config)

        mock_client = AsyncMock()
        cast(Any, mock_client).messages = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock()
        request.json = AsyncMock(
            return_value={"model": "session", "messages": [{"role": "user", "content": "Hi"}]}
        )

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify model was replaced
        call_args = mock_client.messages.call_args[0][0]
        assert call_args["model"] == "claude-sonnet-4-20250514"

    @pytest.mark.asyncio
    async def test_model_preserved_when_explicit(self, config: AnthropicMessagesConfig) -> None:
        """Test explicit model is preserved, not overridden."""
        server = AnthropicMessagesServer(config)

        mock_client = AsyncMock()
        cast(Any, mock_client).messages = AsyncMock(
            return_value={"id": "test", "choices": [{"message": {"content": "Hi"}}]}
        )
        server.client = mock_client

        request = MagicMock()
        request.json = AsyncMock(
            return_value={"model": "claude-opus-4", "messages": [{"role": "user", "content": "Hi"}]}
        )

        response = await server._handle_chat_completions(request)
        assert response.status == 200

        # Verify user-specified model was preserved
        call_args = mock_client.messages.call_args[0][0]
        assert call_args["model"] == "claude-opus-4"
