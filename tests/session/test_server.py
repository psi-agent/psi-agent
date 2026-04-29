"""Tests for server module."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from psi_agent.session.config import SessionConfig
from psi_agent.session.server import SessionServer


@pytest.fixture
def config():
    """Create test config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tools_dir = os.path.join(tmpdir, "tools")
        os.makedirs(tools_dir)

        yield SessionConfig(
            channel_socket=os.path.join(tmpdir, "channel.sock"),
            ai_socket=os.path.join(tmpdir, "ai.sock"),
            workspace=tmpdir,
            history_file=None,
        )


def test_session_server_init(config):
    """Test SessionServer initialization."""
    server = SessionServer(config)
    assert server.config == config
    assert server.runner is None


def test_session_server_routes(config):
    """Test SessionServer routes setup."""
    server = SessionServer(config)
    # Check routes are registered
    routes = list(server.app.router.routes())
    assert len(routes) >= 1


def test_filter_for_channel(config):
    """Test response filtering for channel."""
    server = SessionServer(config)

    full_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello",
                    "tool_calls": [{"id": "123", "function": {"name": "test"}}],
                },
                "finish_reason": "stop",
            }
        ],
        "model": "session",
    }

    filtered = server._filter_for_channel(full_response)

    assert "tool_calls" not in filtered["choices"][0]["message"]
    assert filtered["choices"][0]["message"]["content"] == "Hello"
    assert filtered["choices"][0]["message"]["role"] == "assistant"


def test_filter_for_channel_multiple_choices(config):
    """Test filtering multiple choices."""
    server = SessionServer(config)

    full_response = {
        "choices": [
            {"message": {"role": "assistant", "content": "First"}, "finish_reason": "stop"},
            {"message": {"role": "assistant", "content": "Second"}, "finish_reason": "stop"},
        ],
        "model": "session",
    }

    filtered = server._filter_for_channel(full_response)

    assert len(filtered["choices"]) == 2


def test_filter_for_channel_empty_content(config):
    """Test filtering with empty content."""
    server = SessionServer(config)

    full_response = {
        "choices": [
            {"message": {"role": "assistant", "content": None}, "finish_reason": "stop"},
        ],
        "model": "session",
    }

    filtered = server._filter_for_channel(full_response)

    # The filter uses .get("content", "") which returns None if key exists with None value
    assert filtered["choices"][0]["message"]["content"] is None


@pytest.mark.asyncio
async def test_handle_chat_completions_no_runner(config):
    """Test handling request when runner not initialized."""
    server = SessionServer(config)

    # Create mock request
    mock_request = MagicMock()
    mock_request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "test"}]})

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 500


@pytest.mark.asyncio
async def test_handle_chat_completions_invalid_json(config):
    """Test handling request with invalid JSON."""
    server = SessionServer(config)
    # Set runner to avoid "not ready" error
    from psi_agent.session.runner import SessionRunner

    server.runner = SessionRunner(config)

    # Create mock request that raises JSONDecodeError
    import json

    mock_request = MagicMock()

    async def raise_json_error():
        raise json.JSONDecodeError("test", "test", 0)

    mock_request.json = raise_json_error

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 400


@pytest.mark.asyncio
async def test_handle_chat_completions_no_messages(config):
    """Test handling request with no messages."""
    server = SessionServer(config)
    from psi_agent.session.runner import SessionRunner

    server.runner = SessionRunner(config)

    mock_request = MagicMock()
    mock_request.json = AsyncMock(return_value={"messages": []})

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 400


@pytest.mark.asyncio
async def test_handle_chat_completions_no_user_message(config):
    """Test handling request with no user message."""
    server = SessionServer(config)
    from psi_agent.session.runner import SessionRunner

    server.runner = SessionRunner(config)

    mock_request = MagicMock()
    mock_request.json = AsyncMock(
        return_value={"messages": [{"role": "assistant", "content": "Hi"}]}
    )

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 400


@pytest.mark.asyncio
async def test_handle_other_returns_404(config):
    """Test unhandled routes return 404."""
    server = SessionServer(config)

    mock_request = MagicMock()
    mock_request.method = "GET"
    mock_request.path = "/v1/unknown"

    response = await server._handle_other(mock_request)
    assert response.status == 404
