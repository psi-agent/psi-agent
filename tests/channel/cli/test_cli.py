"""Tests for channel CLI module."""

import pytest

from psi_agent.channel.cli.cli import send_message


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
    import inspect

    sig = inspect.signature(send_message)
    params = list(sig.parameters.keys())

    assert "session_socket" in params
    assert "message" in params
    assert "stream" in params
