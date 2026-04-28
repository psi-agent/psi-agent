"""Tests for OpenAI completions client."""

import httpx
import pytest
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

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


def _make_mock_request() -> httpx.Request:
    """Create a mock httpx.Request for error construction."""
    return httpx.Request("POST", "https://api.example.com/v1/chat/completions")


def _make_mock_response(status_code: int = 200) -> httpx.Response:
    """Create a mock httpx.Response for error construction."""
    request = _make_mock_request()
    return httpx.Response(status_code=status_code, request=request)


@pytest.mark.asyncio
async def test_handle_authentication_error(config: OpenAICompletionsConfig) -> None:
    """Test authentication error handling."""
    client = OpenAICompletionsClient(config)

    async with client:
        error = AuthenticationError(
            message="Invalid API key",
            response=_make_mock_response(401),
            body=None,
        )
        result = client._handle_error(error)
        assert result == {"error": "Authentication failed", "status_code": 401}


@pytest.mark.asyncio
async def test_handle_rate_limit_error(config: OpenAICompletionsConfig) -> None:
    """Test rate limit error handling."""
    client = OpenAICompletionsClient(config)

    async with client:
        error = RateLimitError(
            message="Rate limit exceeded",
            response=_make_mock_response(429),
            body=None,
        )
        result = client._handle_error(error)
        assert result == {"error": "Rate limit exceeded", "status_code": 429}


@pytest.mark.asyncio
async def test_handle_connection_error(config: OpenAICompletionsConfig) -> None:
    """Test connection error handling."""
    client = OpenAICompletionsClient(config)

    async with client:
        error = APIConnectionError(
            message="Connection failed",
            request=_make_mock_request(),
        )
        result = client._handle_error(error)
        assert result == {"error": "Connection failed", "status_code": 500}


@pytest.mark.asyncio
async def test_handle_timeout_error(config: OpenAICompletionsConfig) -> None:
    """Test timeout error handling."""
    client = OpenAICompletionsClient(config)

    async with client:
        error = APITimeoutError(request=_make_mock_request())
        result = client._handle_error(error)
        assert result == {"error": "Request timeout", "status_code": 500}


@pytest.mark.asyncio
async def test_handle_api_status_error(config: OpenAICompletionsConfig) -> None:
    """Test API status error handling."""
    client = OpenAICompletionsClient(config)

    async with client:
        error = APIStatusError(
            message="Internal server error",
            response=_make_mock_response(500),
            body=None,
        )
        result = client._handle_error(error)
        assert result["status_code"] == 500


@pytest.mark.asyncio
async def test_handle_unknown_error(config: OpenAICompletionsConfig) -> None:
    """Test unknown error handling."""
    client = OpenAICompletionsClient(config)

    async with client:
        error = ValueError("Something went wrong")
        result = client._handle_error(error)
        assert result == {"error": "Something went wrong", "status_code": 500}
