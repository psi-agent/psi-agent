"""Tests for channel CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from psi_agent.channel.cli.cli import (
    Cli,
    _handle_non_streaming,
    _handle_streaming,
    main,
    send_message,
)


class TestCliDataclass:
    """Tests for CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        cli = Cli(
            session_socket="/tmp/test.sock",
            message="Hello, world!",
        )
        assert cli.session_socket == "/tmp/test.sock"
        assert cli.message == "Hello, world!"
        assert cli.stream is True  # default

    def test_cli_with_no_stream(self) -> None:
        """Test CLI with stream=False option."""
        cli = Cli(
            session_socket="/tmp/test.sock",
            message="Hello",
            stream=False,
        )
        assert cli.stream is False

    def test_cli_message_attribute(self) -> None:
        """Test CLI message attribute."""
        cli = Cli(
            session_socket="/tmp/test.sock",
            message="Test message content",
        )
        assert cli.message == "Test message content"


class TestSendMessageFunction:
    """Tests for send_message function signature."""

    def test_send_message_signature(self) -> None:
        """Test send_message function exists with correct signature."""
        import inspect

        sig = inspect.signature(send_message)
        params = list(sig.parameters.keys())

        assert "session_socket" in params
        assert "message" in params
        assert "stream" in params

        # Check default value for stream
        assert sig.parameters["stream"].default is True

    @pytest.mark.asyncio
    async def test_send_message_non_streaming_success(self) -> None:
        """Test send_message with non-streaming response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Test response"}}]}
        )

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = MagicMock(return_value=AsyncMock())
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await send_message("/tmp/test.sock", "Hello", stream=False)
            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self) -> None:
        """Test send_message handles connection error."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = MagicMock(
                side_effect=aiohttp.ClientConnectorError(MagicMock(), OSError())
            )

            mock_session_class.return_value = mock_session

            result = await send_message("/tmp/test.sock", "Hello")
            assert result.startswith("Error:")

    @pytest.mark.asyncio
    async def test_send_message_http_error(self) -> None:
        """Test send_message handles HTTP error response."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = MagicMock(return_value=AsyncMock())
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

            mock_session_class.return_value = mock_session

            result = await send_message("/tmp/test.sock", "Hello", stream=False)
            assert result.startswith("Error:")


class TestCliMain:
    """Tests for CLI main function."""

    def test_main_exists(self) -> None:
        """Test main function exists."""
        assert callable(main)

    @patch("psi_agent.channel.cli.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main function calls tyro.cli."""
        main()
        mock_cli.assert_called_once()


class TestHandleNonStreaming:
    """Tests for _handle_non_streaming function."""

    def test_function_exists(self) -> None:
        """Test _handle_non_streaming function exists."""
        assert callable(_handle_non_streaming)

    @pytest.mark.asyncio
    async def test_handle_non_streaming_with_content(self) -> None:
        """Test _handle_non_streaming extracts content correctly."""
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Hello world"}}]}
        )

        result = await _handle_non_streaming(mock_response)
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_handle_non_streaming_empty_choices(self) -> None:
        """Test _handle_non_streaming with empty choices."""
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"choices": []})

        result = await _handle_non_streaming(mock_response)
        assert result == ""

    @pytest.mark.asyncio
    async def test_handle_non_streaming_no_message_content(self) -> None:
        """Test _handle_non_streaming with missing message content."""
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {}}]})

        result = await _handle_non_streaming(mock_response)
        assert result == ""


class TestHandleStreaming:
    """Tests for _handle_streaming function."""

    def test_function_exists(self) -> None:
        """Test _handle_streaming function exists."""
        assert callable(_handle_streaming)

    @pytest.mark.asyncio
    async def test_handle_streaming_with_content(self) -> None:
        """Test _handle_streaming processes streaming chunks."""
        chunks = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n',
            b'data: {"choices": [{"delta": {"content": " world"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for chunk in chunks:
                yield chunk

        mock_response = AsyncMock()
        mock_response.content = async_iter()

        result = await _handle_streaming(mock_response)
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_handle_streaming_with_reasoning(self) -> None:
        """Test _handle_streaming handles reasoning field."""
        chunks = [
            b'data: {"choices": [{"delta": {"reasoning": "thinking..."}}]}\n',
            b'data: {"choices": [{"delta": {"content": "Answer"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for chunk in chunks:
                yield chunk

        mock_response = AsyncMock()
        mock_response.content = async_iter()

        result = await _handle_streaming(mock_response)
        assert result == "Answer"

    @pytest.mark.asyncio
    async def test_handle_streaming_empty_lines(self) -> None:
        """Test _handle_streaming skips empty lines."""
        chunks = [
            b"\n",
            b'data: {"choices": [{"delta": {"content": "test"}}]}\n',
            b"\n",
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for chunk in chunks:
                yield chunk

        mock_response = AsyncMock()
        mock_response.content = async_iter()

        result = await _handle_streaming(mock_response)
        assert result == "test"

    @pytest.mark.asyncio
    async def test_handle_streaming_invalid_json(self) -> None:
        """Test _handle_streaming handles invalid JSON."""
        chunks = [
            b"data: invalid json\n",
            b'data: {"choices": [{"delta": {"content": "valid"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for chunk in chunks:
                yield chunk

        mock_response = AsyncMock()
        mock_response.content = async_iter()

        result = await _handle_streaming(mock_response)
        assert result == "valid"


class TestCliCall:
    """Tests for CLI __call__ method."""

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("sys.exit")
    def test_cli_call_success(self, mock_exit: MagicMock, mock_run: MagicMock) -> None:
        """Test CLI __call__ with successful response."""
        mock_run.return_value = "Success response"

        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=False)
        cli()

        mock_run.assert_called_once()
        mock_exit.assert_not_called()

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("sys.exit")
    def test_cli_call_error(self, mock_exit: MagicMock, mock_run: MagicMock) -> None:
        """Test CLI __call__ with error response."""
        mock_run.return_value = "Error: Connection failed"

        cli = Cli(session_socket="/tmp/test.sock", message="Hello")
        cli()

        mock_exit.assert_called_once_with(1)
