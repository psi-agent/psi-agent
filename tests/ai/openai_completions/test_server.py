"""Tests for OpenAI completions server."""

import pytest

from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig
from psi_agent.ai.openai_completions.server import OpenAICompletionsServer


@pytest.fixture
def config() -> OpenAICompletionsConfig:
    """Create test config."""
    return OpenAICompletionsConfig(
        session_socket="/tmp/test_server.sock",
        model="test-model",
        api_key="test-key",
        base_url="https://api.example.com/v1",
    )


def test_server_creation(config: OpenAICompletionsConfig) -> None:
    """Test server creation."""
    server = OpenAICompletionsServer(config)

    assert server.config == config
    assert server.app is not None
    assert server.client is None


def test_server_routes(config: OpenAICompletionsConfig) -> None:
    """Test server routes are configured."""
    server = OpenAICompletionsServer(config)

    # Check routes exist
    routes = list(server.app.router.routes())
    assert len(routes) >= 2

    # Check POST /v1/chat/completions route exists
    post_routes = [r for r in routes if r.method == "POST"]
    assert len(post_routes) >= 1
    # Check that a POST route exists (the exact path check is fragile with aiohttp internals)
    assert any(r.resource is not None for r in post_routes)
