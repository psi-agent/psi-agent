"""Tests for REPL channel client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from psi_agent.channel.repl.client import ReplClient
from psi_agent.channel.repl.config import ReplConfig


class TestReplClient:
    """Tests for ReplClient."""

    @pytest.fixture
    def config(self) -> ReplConfig:
        """Create test config."""
        return ReplConfig(session_socket="/tmp/test.sock")

    @pytest.fixture
    def client(self, config: ReplConfig) -> ReplClient:
        """Create test client."""
        return ReplClient(config)

    @pytest.mark.asyncio
    async def test_context_manager(self, client: ReplClient) -> None:
        """Test async context manager protocol."""
        with (
            patch("aiohttp.UnixConnector") as mock_connector,
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_connector_instance = AsyncMock()
            mock_connector_instance.close = AsyncMock()
            mock_connector.return_value = mock_connector_instance

            mock_session_instance = AsyncMock()
            mock_session_instance.close = AsyncMock()
            mock_session.return_value = mock_session_instance

            async with client:
                assert client._session is not None
                assert client._connector is not None

            assert client._session is None
            assert client._connector is None

    @pytest.mark.asyncio
    async def test_send_message_success(self, client: ReplClient) -> None:
        """Test successful message sending."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Hello!"}}]}
        )

        with (
            patch("aiohttp.UnixConnector") as mock_connector,
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_connector_instance = AsyncMock()
            mock_connector_instance.close = AsyncMock()
            mock_connector.return_value = mock_connector_instance

            mock_session_instance = MagicMock()
            mock_session_instance.post = MagicMock(
                return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_response))
            )
            mock_session_instance.close = AsyncMock()
            mock_session.return_value = mock_session_instance

            async with client:
                result = await client.send_message("Hi")

                assert result == "Hello!"

    @pytest.mark.asyncio
    async def test_send_message_error_status(self, client: ReplClient) -> None:
        """Test handling error status from session."""
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal error")

        with (
            patch("aiohttp.UnixConnector") as mock_connector,
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_connector_instance = AsyncMock()
            mock_connector_instance.close = AsyncMock()
            mock_connector.return_value = mock_connector_instance

            mock_session_instance = MagicMock()
            mock_session_instance.post = MagicMock(
                return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_response))
            )
            mock_session_instance.close = AsyncMock()
            mock_session.return_value = mock_session_instance

            async with client:
                result = await client.send_message("Hi")

                assert "Error" in result

    @pytest.mark.asyncio
    async def test_send_message_no_choices(self, client: ReplClient) -> None:
        """Test handling no choices in response."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": []})

        with (
            patch("aiohttp.UnixConnector") as mock_connector,
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_connector_instance = AsyncMock()
            mock_connector_instance.close = AsyncMock()
            mock_connector.return_value = mock_connector_instance

            mock_session_instance = MagicMock()
            mock_session_instance.post = MagicMock(
                return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_response))
            )
            mock_session_instance.close = AsyncMock()
            mock_session.return_value = mock_session_instance

            async with client:
                result = await client.send_message("Hi")

                assert "Error" in result

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self, client: ReplClient) -> None:
        """Test handling connection error."""
        with (
            patch("aiohttp.UnixConnector") as mock_connector,
            patch("aiohttp.ClientSession") as mock_session,
        ):
            mock_connector_instance = AsyncMock()
            mock_connector_instance.close = AsyncMock()
            mock_connector.return_value = mock_connector_instance

            mock_session_instance = MagicMock()
            mock_session_instance.post = MagicMock(
                side_effect=aiohttp.ClientConnectorError(
                    connection_key=MagicMock(), os_error=OSError("Connection failed")
                )
            )
            mock_session_instance.close = AsyncMock()
            mock_session.return_value = mock_session_instance

            async with client:
                result = await client.send_message("Hi")

                assert "Error" in result

    @pytest.mark.asyncio
    async def test_send_message_without_context(self, config: ReplConfig) -> None:
        """Test that send_message raises error without context."""
        client = ReplClient(config)

        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.send_message("Hi")
