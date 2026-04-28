"""Tests for TelegramClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.channel.telegram.client import TelegramClient
from psi_agent.channel.telegram.config import TelegramConfig


@pytest.fixture
def config():
    """Create test config."""
    return TelegramConfig(token="test-token", session_socket="/tmp/test.sock")


@pytest.fixture
def client(config):
    """Create test client."""
    return TelegramClient(config)


class TestTelegramClient:
    """Tests for TelegramClient class."""

    def test_client_creation(self, client, config):
        """Test client can be created."""
        assert client.config == config

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager initializes and cleans up."""
        async with client as c:
            assert c is client
            # Session should be initialized
            assert client._session is not None
            assert client._connector is not None

        # After exit, should be cleaned up
        assert client._session is None
        assert client._connector is None

    @pytest.mark.asyncio
    async def test_send_message_without_context(self, client):
        """Test send_message raises error without context."""
        with pytest.raises(RuntimeError, match="not initialized"):
            await client.send_message("test", "telegram:123")

    @pytest.mark.asyncio
    async def test_send_message_success(self, client):
        """Test send_message sends correct request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Test response"}}]}
        )

        with patch.object(client, "_session", None):
            async with client:
                client._session.post = MagicMock(
                    return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
                )

                result = await client.send_message("Hello", "telegram:123")

                assert result == "Test response"

    @pytest.mark.asyncio
    async def test_send_message_error_status(self, client):
        """Test send_message handles error status."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal error")

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message("Hello", "telegram:123")

            assert result.startswith("Error:")
            assert "500" in result

    @pytest.mark.asyncio
    async def test_send_message_no_choices(self, client):
        """Test send_message handles empty choices."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": []})

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message("Hello", "telegram:123")

            assert result.startswith("Error:")
            assert "No response" in result
