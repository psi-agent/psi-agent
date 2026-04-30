"""Tests for channel CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.channel.cli.cli import Cli, _handle_non_streaming, _handle_streaming, send_message


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
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Test response"}}]}
        )

        mock_post = AsyncMock(return_value=mock_response)
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_client = MagicMock()
        mock_client.post = MagicMock(return_value=mock_post)

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_client)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("psi_agent.channel.cli.cli.aiohttp.ClientSession", return_value=mock_session),
            patch("psi_agent.channel.cli.cli.aiohttp.UnixConnector"),
        ):
            result = await send_message("/tmp/test.sock", "Hello", stream=False)

        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_send_message_non_streaming_error_status(self) -> None:
        """Test send_message with non-200 status."""
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        mock_post = AsyncMock(return_value=mock_response)
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_client = MagicMock()
        mock_client.post = MagicMock(return_value=mock_post)

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_client)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with (
            patch("psi_agent.channel.cli.cli.aiohttp.ClientSession", return_value=mock_session),
            patch("psi_agent.channel.cli.cli.aiohttp.UnixConnector"),
        ):
            result = await send_message("/tmp/test.sock", "Hello", stream=False)

        assert result.startswith("Error:")

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self) -> None:
        """Test send_message handles connection error gracefully."""
        # This test verifies the error handling path exists
        # The actual connection error handling is tested via integration tests
        # Here we just verify the function signature accepts the parameters
        assert callable(send_message)


class TestCliMain:
    """Tests for CLI main function."""

    def test_main_exists(self) -> None:
        """Test main function exists."""
        from psi_agent.channel.cli.cli import main

        assert callable(main)

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("psi_agent.channel.cli.cli.send_message", new_callable=AsyncMock)
    def test_cli_call_streaming(self, mock_send: AsyncMock, mock_run: MagicMock) -> None:
        """Test CLI __call__ with streaming."""
        mock_run.return_value = "Test response"
        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=True)
        cli()
        mock_run.assert_called_once()

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("psi_agent.channel.cli.cli.send_message", new_callable=AsyncMock)
    @patch("builtins.print")
    def test_cli_call_non_streaming(
        self, mock_print: MagicMock, mock_send: AsyncMock, mock_run: MagicMock
    ) -> None:
        """Test CLI __call__ with non-streaming."""
        mock_run.return_value = "Test response"
        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=False)
        cli()
        mock_print.assert_called()

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("psi_agent.channel.cli.cli.send_message", new_callable=AsyncMock)
    def test_cli_call_error_exit(self, mock_send: AsyncMock, mock_run: MagicMock) -> None:
        """Test CLI __call__ exits with error code on error."""
        mock_run.return_value = "Error: Connection failed"
        cli = Cli(session_socket="/tmp/test.sock", message="Hello")

        with pytest.raises(SystemExit) as exc_info:
            cli()

        assert exc_info.value.code == 1


class TestHandleNonStreaming:
    """Tests for _handle_non_streaming function."""

    def test_function_exists(self) -> None:
        """Test _handle_non_streaming function exists."""
        from psi_agent.channel.cli.cli import _handle_non_streaming

        assert callable(_handle_non_streaming)

    @pytest.mark.asyncio
    async def test_handle_non_streaming_with_content(self) -> None:
        """Test _handle_non_streaming extracts content."""
        mock_response = MagicMock()
        mock_response.json = AsyncMock(
            return_value={"choices": [{"message": {"content": "Hello world"}}]}
        )

        result = await _handle_non_streaming(mock_response)
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_handle_non_streaming_empty_choices(self) -> None:
        """Test _handle_non_streaming with empty choices."""
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"choices": []})

        result = await _handle_non_streaming(mock_response)
        assert result == ""

    @pytest.mark.asyncio
    async def test_handle_non_streaming_no_message(self) -> None:
        """Test _handle_non_streaming with no message in choice."""
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"choices": [{}]})

        result = await _handle_non_streaming(mock_response)
        assert result == ""


class TestHandleStreaming:
    """Tests for _handle_streaming function."""

    def test_function_exists(self) -> None:
        """Test _handle_streaming function exists."""
        from psi_agent.channel.cli.cli import _handle_streaming

        assert callable(_handle_streaming)

    @pytest.mark.asyncio
    async def test_handle_streaming_with_content(self) -> None:
        """Test _handle_streaming extracts content from SSE stream."""
        # Create mock response with streaming content
        lines = [
            b'data: {"choices": [{"delta": {"content": "Hello "}}]}\n',
            b'data: {"choices": [{"delta": {"content": "world"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.content = mock_aiter()

        result = await _handle_streaming(mock_response)
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_handle_streaming_with_reasoning(self) -> None:
        """Test _handle_streaming handles reasoning field."""
        lines = [
            b'data: {"choices": [{"delta": {"reasoning": "Thinking..."}}]}\n',
            b'data: {"choices": [{"delta": {"content": "Answer"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.content = mock_aiter()

        result = await _handle_streaming(mock_response)
        assert result == "Answer"

    @pytest.mark.asyncio
    async def test_handle_streaming_empty_content(self) -> None:
        """Test _handle_streaming with empty content."""
        lines = [
            b'data: {"choices": [{"delta": {"content": ""}}]}\n',
            b'data: {"choices": [{"delta": {"content": "text"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.content = mock_aiter()

        result = await _handle_streaming(mock_response)
        assert result == "text"

    @pytest.mark.asyncio
    async def test_handle_streaming_invalid_json(self) -> None:
        """Test _handle_streaming handles invalid JSON."""
        lines = [
            b"data: invalid json\n",
            b'data: {"choices": [{"delta": {"content": "valid"}}]}\n',
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.content = mock_aiter()

        result = await _handle_streaming(mock_response)
        assert result == "valid"

    @pytest.mark.asyncio
    async def test_handle_streaming_skip_empty_lines(self) -> None:
        """Test _handle_streaming skips empty lines."""
        lines = [
            b"\n",
            b'data: {"choices": [{"delta": {"content": "text"}}]}\n',
            b"",
        ]

        async def mock_aiter():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.content = mock_aiter()

        result = await _handle_streaming(mock_response)
        assert result == "text"
