"""Tests for OpenAI completions client."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError

from psi_agent.ai.openai_completions.client import OpenAICompletionsClient
from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig


class TestOpenAICompletionsClient:
    """Tests for OpenAICompletionsClient."""

    @pytest.fixture
    def config(self) -> OpenAICompletionsConfig:
        """Create test config."""
        return OpenAICompletionsConfig(
            session_socket="/tmp/test.sock",
            model="test-model",
            api_key="test-key",
            base_url="https://api.example.com/v1",
        )

    @pytest.fixture
    def client(self, config: OpenAICompletionsConfig) -> OpenAICompletionsClient:
        """Create test client."""
        return OpenAICompletionsClient(config)

    @pytest.mark.asyncio
    async def test_context_manager(self, client: OpenAICompletionsClient) -> None:
        """Test async context manager protocol."""
        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                assert client._client is not None

            assert client._client is None

    @pytest.mark.asyncio
    async def test_non_streaming_request(self, client: OpenAICompletionsClient) -> None:
        """Test non-streaming request."""
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.model_dump = MagicMock(return_value={"id": "chatcmpl-123", "choices": []})

        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Type narrowing: non-streaming returns dict
                assert not isinstance(result, AsyncGenerator)
                assert result["id"] == "chatcmpl-123"

    @pytest.mark.asyncio
    async def test_streaming_request(self, client: OpenAICompletionsClient) -> None:
        """Test streaming request."""
        mock_chunk = MagicMock()
        mock_chunk.model_dump_json = MagicMock(return_value='{"id": "chatcmpl-123"}')

        async def mock_stream():
            yield mock_chunk

        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_stream())
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                stream_gen = cast(AsyncGenerator[str], result)
                chunks = []
                async for chunk in stream_gen:
                    chunks.append(chunk)

                # Should have 2 chunks: the response and [DONE]
                assert len(chunks) == 2
                assert "chatcmpl-123" in chunks[0]
                assert "[DONE]" in chunks[1]

    @pytest.mark.asyncio
    async def test_model_injection(self, client: OpenAICompletionsClient) -> None:
        """Test model is injected if not provided."""
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.model_dump = MagicMock(return_value={"id": "chatcmpl-123"})

        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                await client.chat_completions(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Check that model was injected
                call_kwargs = mock_instance.chat.completions.create.call_args
                assert call_kwargs[1]["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_authentication_error(self, client: OpenAICompletionsClient) -> None:
        """Test authentication error handling."""
        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(
                side_effect=AuthenticationError(
                    message="Invalid API key",
                    response=MagicMock(status_code=401),
                    body=None,
                )
            )
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
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
    async def test_rate_limit_error(self, client: OpenAICompletionsClient) -> None:
        """Test rate limit error handling."""
        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(
                side_effect=RateLimitError(
                    message="Rate limit exceeded",
                    response=MagicMock(status_code=429),
                    body=None,
                )
            )
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
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
    async def test_connection_error(self, client: OpenAICompletionsClient) -> None:
        """Test connection error handling."""
        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(
                side_effect=APIConnectionError(request=MagicMock())
            )
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
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

    @pytest.mark.asyncio
    async def test_timeout_error(self, client: OpenAICompletionsClient) -> None:
        """Test timeout error handling."""
        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(
                side_effect=APITimeoutError(request=MagicMock())
            )
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
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

    @pytest.mark.asyncio
    async def test_reasoning_effort_passthrough(self, client: OpenAICompletionsClient) -> None:
        """Test reasoning_effort parameter is passed through to upstream API."""
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.model_dump = MagicMock(return_value={"id": "chatcmpl-123"})

        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                await client.chat_completions(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "reasoning_effort": "high",
                    },
                    stream=False,
                )

                # Check that reasoning_effort was passed through
                call_kwargs = mock_instance.chat.completions.create.call_args
                assert call_kwargs[1]["reasoning_effort"] == "high"
