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


class TestCliDataclass:
    """Tests for CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        # Test instantiation
        cli = Cli(session_socket="/tmp/test.sock", message="Hello")
        assert cli.session_socket == "/tmp/test.sock"
        assert cli.message == "Hello"
        assert cli.stream is False  # default

    def test_cli_with_stream(self) -> None:
        """Test CLI with stream option."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=True)
        assert cli.stream is True
