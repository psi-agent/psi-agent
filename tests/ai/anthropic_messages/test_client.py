"""Tests for Anthropic Messages client."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.ai.anthropic_messages.client import AnthropicMessagesClient
from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig


class TestAnthropicMessagesClient:
    """Tests for AnthropicMessagesClient."""

    @pytest.fixture
    def config(self) -> AnthropicMessagesConfig:
        """Create test config."""
        return AnthropicMessagesConfig(
            session_socket="/tmp/test.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
        )

    @pytest.fixture
    def client(self, config: AnthropicMessagesConfig) -> AnthropicMessagesClient:
        """Create test client."""
        return AnthropicMessagesClient(config)

    @pytest.mark.asyncio
    async def test_context_manager(self, client: AnthropicMessagesClient) -> None:
        """Test async context manager protocol."""
        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                assert client._client is not None

            assert client._client is None

    @pytest.mark.asyncio
    async def test_non_streaming_request(self, client: AnthropicMessagesClient) -> None:
        """Test non-streaming request returns OpenAI format."""
        mock_response = MagicMock()
        mock_response.id = "msg_123"
        mock_response.model_dump = MagicMock(
            return_value={
                "id": "msg_123",
                "model": "claude-3",
                "content": [{"type": "text", "text": "Hello!"}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
        )

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.create = AsyncMock(return_value=mock_response)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Type narrowing: non-streaming returns dict
                assert not isinstance(result, AsyncGenerator)
                # Check OpenAI format
                assert result["id"] == "msg_123"
                assert result["object"] == "chat.completion"
                assert "choices" in result
                assert result["choices"][0]["message"]["content"] == "Hello!"

    @pytest.mark.asyncio
    async def test_model_injection(self, client: AnthropicMessagesClient) -> None:
        """Test model is injected if not provided."""
        mock_response = MagicMock()
        mock_response.id = "msg_123"
        mock_response.model_dump = MagicMock(
            return_value={
                "id": "msg_123",
                "content": [{"type": "text", "text": "Response"}],
            }
        )

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.create = AsyncMock(return_value=mock_response)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Check that model was injected
                call_kwargs = mock_instance.messages.create.call_args
                assert call_kwargs[1]["model"] == "claude-sonnet-4-20250514"

    @pytest.mark.asyncio
    async def test_authentication_error(self, client: AnthropicMessagesClient) -> None:
        """Test authentication error handling."""
        from anthropic import AuthenticationError

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.create = AsyncMock(
                side_effect=AuthenticationError(
                    message="Invalid API key",
                    response=MagicMock(status_code=401),
                    body={"error": {"message": "Invalid API key"}},
                )
            )
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Type narrowing: non-streaming returns dict
                assert not isinstance(result, AsyncGenerator)
                assert "error" in result
                assert result["status_code"] == 401

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client: AnthropicMessagesClient) -> None:
        """Test rate limit error handling."""
        from anthropic import RateLimitError

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.create = AsyncMock(
                side_effect=RateLimitError(
                    message="Rate limit exceeded",
                    response=MagicMock(status_code=429),
                    body={"error": {"message": "Rate limit exceeded"}},
                )
            )
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Type narrowing: non-streaming returns dict
                assert not isinstance(result, AsyncGenerator)
                assert "error" in result
                assert result["status_code"] == 429

    @pytest.mark.asyncio
    async def test_connection_error(self, client: AnthropicMessagesClient) -> None:
        """Test connection error handling."""
        from anthropic import APIConnectionError

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.create = AsyncMock(
                side_effect=APIConnectionError(request=MagicMock())
            )
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Type narrowing: non-streaming returns dict
                assert not isinstance(result, AsyncGenerator)
                assert "error" in result
                assert result["status_code"] == 500
