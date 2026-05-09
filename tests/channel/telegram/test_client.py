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

    @pytest.mark.asyncio
    async def test_send_message_stream_without_context(self, client):
        """Test send_message_stream raises error without context."""
        with pytest.raises(RuntimeError, match="not initialized"):
            await client.send_message_stream("test", "telegram:123")

    @pytest.mark.asyncio
    async def test_send_message_stream_success(self, client):
        """Test send_message_stream sends correct request and parses SSE."""
        # Mock SSE response
        sse_lines = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " world"}}]}',
            b"data: [DONE]",
        ]

        # Create async iterator
        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        chunks_received: list[str] = []

        def on_chunk(chunk: str) -> None:
            chunks_received.append(chunk)

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message_stream("Hi", "telegram:123", on_chunk)

            assert result == "Hello world"
            assert chunks_received == ["Hello", " world"]

    @pytest.mark.asyncio
    async def test_send_message_stream_error_status(self, client):
        """Test send_message_stream handles error status."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal error")

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message_stream("Hi", "telegram:123")

            assert result.startswith("Error:")
            assert "500" in result

    @pytest.mark.asyncio
    async def test_send_message_stream_without_callback(self, client):
        """Test send_message_stream works without callback."""
        sse_lines = [
            b'data: {"choices": [{"delta": {"content": "Test"}}]}',
            b"data: [DONE]",
        ]

        # Create async iterator
        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message_stream("Hi", "telegram:123")

            assert result == "Test"

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self, client):
        """Test send_message handles connection error."""
        import aiohttp

        async with client:
            client._session.post = MagicMock(
                side_effect=aiohttp.ClientConnectorError(
                    MagicMock(), MagicMock(connection_key="test")
                )
            )

            result = await client.send_message("Hello", "telegram:123")

            assert result.startswith("Error:")
            assert "connect" in result.lower()

    @pytest.mark.asyncio
    async def test_send_message_client_error(self, client):
        """Test send_message handles generic client error."""
        import aiohttp

        async with client:
            client._session.post = MagicMock(side_effect=aiohttp.ClientError("Network error"))

            result = await client.send_message("Hello", "telegram:123")

            assert result.startswith("Error:")
            assert "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_send_message_timeout(self, client):
        """Test send_message handles timeout."""
        async with client:
            client._session.post = MagicMock(side_effect=TimeoutError())

            result = await client.send_message("Hello", "telegram:123")

            assert result.startswith("Error:")
            assert "timeout" in result.lower()

    @pytest.mark.asyncio
    async def test_send_message_stream_connection_error(self, client):
        """Test send_message_stream handles connection error."""
        import aiohttp

        async with client:
            client._session.post = MagicMock(
                side_effect=aiohttp.ClientConnectorError(
                    MagicMock(), MagicMock(connection_key="test")
                )
            )

            result = await client.send_message_stream("Hi", "telegram:123")

            assert result.startswith("Error:")
            assert "connect" in result.lower()

    @pytest.mark.asyncio
    async def test_send_message_stream_client_error(self, client):
        """Test send_message_stream handles generic client error."""
        import aiohttp

        async with client:
            client._session.post = MagicMock(side_effect=aiohttp.ClientError("Network error"))

            result = await client.send_message_stream("Hi", "telegram:123")

            assert result.startswith("Error:")
            assert "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_send_message_stream_timeout(self, client):
        """Test send_message_stream handles timeout."""
        async with client:
            client._session.post = MagicMock(side_effect=TimeoutError())

            result = await client.send_message_stream("Hi", "telegram:123")

            assert result.startswith("Error:")
            assert "timeout" in result.lower()

    @pytest.mark.asyncio
    async def test_send_message_stream_invalid_json(self, client):
        """Test send_message_stream handles invalid JSON in SSE."""
        sse_lines = [
            b"data: invalid json",
            b"data: [DONE]",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message_stream("Hi", "telegram:123")

            # Should return empty string since no valid content was parsed
            assert result == ""

    @pytest.mark.asyncio
    async def test_send_message_stream_empty_lines(self, client):
        """Test send_message_stream skips empty lines."""
        sse_lines = [
            b"",
            b'data: {"choices": [{"delta": {"content": "Test"}}]}',
            b"",
            b"data: [DONE]",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with client:
            client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await client.send_message_stream("Hi", "telegram:123")

            assert result == "Test"


class TestTelegramClientNullEmptyContent:
    """Tests for TelegramClient handling null/empty content in responses."""

    @pytest.fixture
    def null_config(self):
        """Create test config."""
        return TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    @pytest.fixture
    def null_client(self, null_config):
        """Create test client."""
        return TelegramClient(null_config)

    @pytest.mark.asyncio
    async def test_streaming_null_content_in_delta_skipped(self, null_client):
        """Null content in streaming delta is skipped (not appended)."""
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":null}}]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with null_client:
            null_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await null_client.send_message_stream("Hi", "telegram:123")
            assert result == "Hello"

    @pytest.mark.asyncio
    async def test_streaming_empty_string_content_in_delta_handled(self, null_client):
        """Empty string content in streaming delta is handled."""
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":""}}]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with null_client:
            null_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await null_client.send_message_stream("Hi", "telegram:123")
            assert result == "Hello"

    @pytest.mark.asyncio
    async def test_non_streaming_null_content_returns_empty_string(self, null_client):
        """Null content in non-streaming response returns empty string."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": None}}]})

        async with null_client:
            null_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await null_client.send_message("Hi", "telegram:123")
            assert result == ""


class TestTelegramClientReasoningAndMissingFields:
    """Tests for TelegramClient handling reasoning field and missing fields."""

    @pytest.fixture
    def missing_config(self):
        """Create test config."""
        return TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    @pytest.fixture
    def missing_client(self, missing_config):
        """Create test client."""
        return TelegramClient(missing_config)

    @pytest.mark.asyncio
    async def test_streaming_reasoning_field_handled(self, missing_client):
        """Reasoning field in streaming delta is handled without crash."""
        sse_lines = [
            b'data: {"choices":[{"delta":{"reasoning":"thinking...","content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with missing_client:
            missing_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await missing_client.send_message_stream("Hi", "telegram:123")
            assert result == "Hello"

    @pytest.mark.asyncio
    async def test_streaming_empty_choices_list_skipped(self, missing_client):
        """Empty choices list in streaming chunk is skipped."""
        sse_lines = [
            b'data: {"choices":[]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with missing_client:
            missing_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await missing_client.send_message_stream("Hi", "telegram:123")
            assert result == "Hello"

    @pytest.mark.asyncio
    async def test_streaming_missing_delta_key_no_crash(self, missing_client):
        """Missing delta key in streaming chunk does not crash."""
        sse_lines = [
            b'data: {"choices":[{}]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with missing_client:
            missing_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            result = await missing_client.send_message_stream("Hi", "telegram:123")
            assert result == "Hello"


class TestTelegramClientUserId:
    """Tests for TelegramClient user_id field in request body."""

    @pytest.fixture
    def user_config(self):
        """Create test config."""
        return TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    @pytest.fixture
    def user_client(self, user_config):
        """Create test client."""
        return TelegramClient(user_config)

    @pytest.mark.asyncio
    async def test_send_message_includes_user_field(self, user_client):
        """send_message includes user field in request body."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Hello"}}]}
        )

        async with user_client:
            user_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            await user_client.send_message("Hi", "telegram:123")

            # Verify post was called with json containing user field
            call_args = user_client._session.post.call_args
            json_body = call_args.kwargs.get("json", {})
            assert "user" in json_body
            assert json_body["user"] == "telegram:123"

    @pytest.mark.asyncio
    async def test_send_message_stream_includes_user_field(self, user_client):
        """send_message_stream includes user field in request body."""
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        async with user_client:
            user_client._session.post = MagicMock(
                return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))
            )

            await user_client.send_message_stream("Hi", "telegram:123")

            # Verify post was called with json containing user field
            call_args = user_client._session.post.call_args
            json_body = call_args.kwargs.get("json", {})
            assert "user" in json_body
            assert json_body["user"] == "telegram:123"
