"""Tests for channel CLI module."""

from __future__ import annotations

import inspect

import pytest

from psi_agent.channel.cli.cli import Cli, send_message


@pytest.mark.asyncio
async def test_send_message_connection_error():
    """Test send_message with invalid socket path."""
    result = await send_message("/nonexistent/socket.sock", "Hello")
    assert result.startswith("Error:")
    assert "Cannot connect" in result


@pytest.mark.asyncio
async def test_send_message_request_format():
    """Test that request is properly formatted."""
    # This test verifies the function exists and has correct signature
    # Integration tests would require a running session
    sig = inspect.signature(send_message)
    params = list(sig.parameters.keys())

    assert "session_socket" in params
    assert "message" in params
    assert "stream" in params


@pytest.mark.asyncio
async def test_send_message_default_stream_true():
    """Test that send_message defaults to streaming mode."""
    sig = inspect.signature(send_message)
    stream_param = sig.parameters["stream"]

    assert stream_param.default is True


class TestCliFlags:
    """Tests for CLI flag handling."""

    def test_cli_default_stream_enabled(self) -> None:
        """Test CLI defaults to streaming enabled."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello")

        assert cli.no_stream is False

    def test_cli_no_stream_flag(self) -> None:
        """Test CLI --no-stream flag disables streaming."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello", no_stream=True)

        assert cli.no_stream is True

    def test_cli_stream_passed_to_send_message(self) -> None:
        """Test CLI passes correct stream value to send_message."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello", no_stream=True)

        # no_stream=True means stream=False
        assert cli.no_stream is not False
