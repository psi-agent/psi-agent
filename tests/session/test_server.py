"""Tests for server module."""

import tempfile
from pathlib import Path

import pytest

from psi_agent.session.config import SessionConfig
from psi_agent.session.server import SessionServer


@pytest.fixture
def config():
    """Create test config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "tools").mkdir()

        yield SessionConfig(
            channel_socket=str(workspace / "channel.sock"),
            ai_socket=str(workspace / "ai.sock"),
            workspace=str(workspace),
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
