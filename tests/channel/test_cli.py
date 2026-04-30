"""Tests for channel CLI module."""

from __future__ import annotations

from psi_agent.channel.cli.cli import Cli, send_message


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


class TestCliMain:
    """Tests for CLI main function."""

    def test_main_exists(self) -> None:
        """Test main function exists."""
        from psi_agent.channel.cli.cli import main

        assert callable(main)


class TestHandleNonStreaming:
    """Tests for _handle_non_streaming function."""

    def test_function_exists(self) -> None:
        """Test _handle_non_streaming function exists."""
        from psi_agent.channel.cli.cli import _handle_non_streaming

        assert callable(_handle_non_streaming)


class TestHandleStreaming:
    """Tests for _handle_streaming function."""

    def test_function_exists(self) -> None:
        """Test _handle_streaming function exists."""
        from psi_agent.channel.cli.cli import _handle_streaming

        assert callable(_handle_streaming)
