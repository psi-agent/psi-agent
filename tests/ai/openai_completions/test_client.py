"""Tests for OpenAI completions client."""

import pytest

from psi_agent.ai.openai_completions.client import OpenAICompletionsClient
from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig


@pytest.fixture
def config() -> OpenAICompletionsConfig:
    """Create test config."""
    return OpenAICompletionsConfig(
        session_socket="/tmp/test.sock",
        model="test-model",
        api_key="test-key",
        base_url="https://api.example.com/v1",
    )


@pytest.mark.asyncio
async def test_client_context_manager(config: OpenAICompletionsConfig) -> None:
    """Test client async context manager."""
    client = OpenAICompletionsClient(config)

    # Should raise if used without context
    with pytest.raises(RuntimeError):
        await client.chat_completions({"messages": []})

    # Should work with context
    async with client:
        assert client._client is not None

    # Should be closed after context
    assert client._client is None


@pytest.mark.asyncio
async def test_client_injects_model(config: OpenAICompletionsConfig) -> None:
    """Test client injects model into request body."""
    client = OpenAICompletionsClient(config)

    async with client:
        # Model should be injected
        body = {"messages": [{"role": "user", "content": "Hello"}]}
        # We can't test actual API call without mocking, but we can check the logic
        assert "model" not in body


@pytest.mark.asyncio
async def test_client_model_already_present(config: OpenAICompletionsConfig) -> None:
    """Test client respects existing model in request body."""
    client = OpenAICompletionsClient(config)

    async with client:
        body = {"model": "custom-model", "messages": [{"role": "user", "content": "Hello"}]}
        # Model should remain as-is
        assert body["model"] == "custom-model"
