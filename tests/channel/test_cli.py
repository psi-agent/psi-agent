"""Tests for channel CLI client module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from psi_agent.channel.cli.client import CliClient
from psi_agent.channel.cli.config import CliConfig


class TestCliClientAsyncContext:
    """Tests for CLI client async context manager."""

    @pytest.mark.asyncio
    async def test_client_context_manager(self) -> None:
        """Test client can be used as async context manager."""
        config = CliConfig(session_socket="/tmp/test.sock")
        client = CliClient(config)

        async with client:
            assert client._session is not None
            assert client._connector is not None

        # After exit, resources should be cleaned
        assert client._session is None
        assert client._connector is None

    @pytest.mark.asyncio
    async def test_client_context_manager_creates_session(self) -> None:
        """Test client creates aiohttp session in context."""
        config = CliConfig(session_socket="/tmp/test.sock")
        client = CliClient(config)

        async with client:
            assert client._session is not None


class TestCliClientSendMessage:
    """Tests for CLI client send_message method."""

    @pytest.mark.asyncio
    async def test_send_message_non_streaming_success(self) -> None:
        """Test send_message with non-streaming response."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Test response"}}]}
        )

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_send_message_non_streaming_error_status(self) -> None:
        """Test send_message with non-200 status."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result.startswith("Error:")

    @pytest.mark.asyncio
    async def test_send_message_includes_model_field(self) -> None:
        """Test that request body includes model field."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        captured_body = {}

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "OK"}}]})

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        def capture_post(url, **kwargs):
            captured_body.update(kwargs.get("json", {}))
            return mock_post

        mock_session = MagicMock()
        mock_session.post = capture_post
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            await client.send_message("Hello")

        assert captured_body.get("model") == "session"

    @pytest.mark.asyncio
    async def test_send_message_non_streaming_no_choices(self) -> None:
        """Test send_message with no choices in response."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": []})

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "Error: No response from session"

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self) -> None:
        """Test send_message handles connection error."""
        import aiohttp

        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        # Create a proper mock for ClientConnectorError
        mock_conn_key = MagicMock()
        mock_os_error = OSError("Connection refused")
        conn_error = aiohttp.ClientConnectorError(mock_conn_key, mock_os_error)

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(side_effect=conn_error)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert "Error: Failed to connect to session" in result

    @pytest.mark.asyncio
    async def test_send_message_client_error(self) -> None:
        """Test send_message handles client error."""
        import aiohttp

        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("Error"))
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result.startswith("Error: Request failed")

    @pytest.mark.asyncio
    async def test_send_message_timeout_error(self) -> None:
        """Test send_message handles timeout error."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(side_effect=TimeoutError())
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "Error: Request timeout"


class TestCliClientStreaming:
    """Tests for CLI client streaming functionality."""

    @pytest.mark.asyncio
    async def test_send_message_streaming_with_content(self) -> None:
        """Test streaming extracts content from SSE stream."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        lines = [
            b'data: {"choices": [{"delta": {"content": "Hello "}}]}\n',
            b'data: {"choices": [{"delta": {"content": "world"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = mock_aiter()

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_send_message_streaming_with_reasoning(self) -> None:
        """Test streaming handles reasoning field."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        lines = [
            b'data: {"choices": [{"delta": {"reasoning": "Thinking..."}}]}\n',
            b'data: {"choices": [{"delta": {"content": "Answer"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = mock_aiter()

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "Answer"

    @pytest.mark.asyncio
    async def test_send_message_streaming_empty_content(self) -> None:
        """Test streaming with empty content string."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        lines = [
            b'data: {"choices": [{"delta": {"content": ""}}]}\n',
            b'data: {"choices": [{"delta": {"content": "text"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = mock_aiter()

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        # Empty string should still be appended
        assert result == "text"

    @pytest.mark.asyncio
    async def test_send_message_streaming_callback(self) -> None:
        """Test streaming invokes callback for each non-empty chunk."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        lines = [
            b'data: {"choices": [{"delta": {"content": "Hello "}}]}\n',
            b'data: {"choices": [{"delta": {"content": "world"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = mock_aiter()

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        chunks_received = []

        async with client:
            client._session = mock_session
            await client.send_message("Hello", on_chunk=lambda c: chunks_received.append(c))

        assert chunks_received == ["Hello ", "world"]

    @pytest.mark.asyncio
    async def test_send_message_streaming_error_status(self) -> None:
        """Test streaming handles error status."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result.startswith("Error: Session returned status")

    @pytest.mark.asyncio
    async def test_send_message_streaming_connection_error(self) -> None:
        """Test streaming handles connection error."""
        import aiohttp

        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        # Create a proper mock for ClientConnectorError
        mock_conn_key = MagicMock()
        mock_os_error = OSError("Connection refused")
        conn_error = aiohttp.ClientConnectorError(mock_conn_key, mock_os_error)

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(side_effect=conn_error)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert "Error: Failed to connect to session" in result

    @pytest.mark.asyncio
    async def test_send_message_streaming_timeout_error(self) -> None:
        """Test streaming handles timeout error."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(side_effect=TimeoutError())
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "Error: Request timeout"

    @pytest.mark.asyncio
    async def test_send_message_streaming_client_error(self) -> None:
        """Test streaming handles client error."""
        import aiohttp

        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("Error"))
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result.startswith("Error: Request failed")

    @pytest.mark.asyncio
    async def test_send_message_streaming_invalid_json(self) -> None:
        """Test streaming handles invalid JSON."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        lines = [
            b"data: invalid json\n",
            b'data: {"choices": [{"delta": {"content": "valid"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = mock_aiter()

        mock_post = MagicMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_post)
        mock_session.close = AsyncMock()

        mock_connector = MagicMock()
        mock_connector.close = AsyncMock()

        async with client:
            client._session = mock_session
            result = await client.send_message("Hello")

        assert result == "valid"
