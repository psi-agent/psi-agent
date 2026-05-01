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

    def test_split_params_sdk_only(self, client: OpenAICompletionsClient) -> None:
        """Test _split_params with only SDK parameters."""
        body = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        sdk_params, extra_params = client._split_params(body)

        assert sdk_params == body
        assert extra_params is None

    def test_split_params_with_thinking(self, client: OpenAICompletionsClient) -> None:
        """Test _split_params with thinking parameter."""
        body = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "thinking": {"type": "enabled"},
        }
        sdk_params, extra_params = client._split_params(body)

        assert sdk_params == {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
        }
        assert extra_params == {"thinking": {"type": "enabled"}}

    def test_split_params_with_reasoning_effort(self, client: OpenAICompletionsClient) -> None:
        """Test _split_params with reasoning_effort parameter."""
        body = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "reasoning_effort": "high",
        }
        sdk_params, extra_params = client._split_params(body)

        assert sdk_params == {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
        }
        assert extra_params == {"reasoning_effort": "high"}

    def test_split_params_with_both_provider_params(self, client: OpenAICompletionsClient) -> None:
        """Test _split_params with both thinking and reasoning_effort."""
        body = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "thinking": {"type": "enabled"},
            "reasoning_effort": "high",
        }
        sdk_params, extra_params = client._split_params(body)

        assert sdk_params == {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
        }
        assert extra_params == {
            "thinking": {"type": "enabled"},
            "reasoning_effort": "high",
        }

    @pytest.mark.asyncio
    async def test_non_streaming_with_thinking_param(self, client: OpenAICompletionsClient) -> None:
        """Test non-streaming request with thinking parameter passes via extra_body."""
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.model_dump = MagicMock(return_value={"id": "chatcmpl-123"})

        with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
            mock_instance = AsyncMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_instance.close = AsyncMock()
            mock_openai.return_value = mock_instance

            async with client:
                result = await client.chat_completions(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "thinking": {"type": "enabled"},
                    },
                    stream=False,
                )

                # Verify extra_body was passed with thinking
                call_kwargs = mock_instance.chat.completions.create.call_args
                assert "extra_body" in call_kwargs[1]
                assert call_kwargs[1]["extra_body"] == {"thinking": {"type": "enabled"}}
                # Verify thinking is NOT in SDK params
                assert "thinking" not in call_kwargs[1]

                # Type narrowing: non-streaming returns dict
                assert not isinstance(result, AsyncGenerator)
                assert result["id"] == "chatcmpl-123"

    @pytest.mark.asyncio
    async def test_streaming_with_reasoning_effort_param(
        self, client: OpenAICompletionsClient
    ) -> None:
        """Test streaming request with reasoning_effort parameter passes via extra_body."""
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
                        "reasoning_effort": "high",
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                stream_gen = cast(AsyncGenerator[str], result)
                chunks = []
                async for chunk in stream_gen:
                    chunks.append(chunk)

                # Verify extra_body was passed with reasoning_effort
                # Note: call_args is only available after consuming the generator
                call_kwargs = mock_instance.chat.completions.create.call_args
                assert "extra_body" in call_kwargs[1]
                assert call_kwargs[1]["extra_body"] == {"reasoning_effort": "high"}
                # Verify reasoning_effort is NOT in SDK params
                assert "reasoning_effort" not in call_kwargs[1]

                assert len(chunks) == 2
