"""Tests for Anthropic Messages server."""

from __future__ import annotations

import tempfile
from pathlib import Path as SyncPath
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig
from psi_agent.ai.anthropic_messages.server import AnthropicMessagesServer


class TestAnthropicMessagesServer:
    """Tests for AnthropicMessagesServer."""

    @pytest.fixture
    def config(self) -> AnthropicMessagesConfig:
        """Create test config."""
        return AnthropicMessagesConfig(
            session_socket="/tmp/test_server.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
        )

    @pytest.fixture
    def server(self, config: AnthropicMessagesConfig) -> AnthropicMessagesServer:
        """Create test server."""
        return AnthropicMessagesServer(config)

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
        import json

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
            socket_path = SyncPath(tmpdir) / "test.sock"
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
