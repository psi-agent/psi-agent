"""Tests for Anthropic Messages client."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import APIConnectionError, AuthenticationError, RateLimitError

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
    async def test_model_session_placeholder_replacement(
        self, client: AnthropicMessagesClient
    ) -> None:
        """Test model 'session' placeholder is replaced with configured model."""
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
                        "model": "session",  # Placeholder should be replaced
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Check that model was replaced
                call_kwargs = mock_instance.messages.create.call_args
                assert call_kwargs[1]["model"] == "claude-sonnet-4-20250514"

    @pytest.mark.asyncio
    async def test_model_not_replaced_when_explicit(self, client: AnthropicMessagesClient) -> None:
        """Test model is not replaced when explicit value (not 'session')."""
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
                        "model": "claude-opus-4",  # Explicit model should be preserved
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=False,
                )

                # Check that model was preserved
                call_kwargs = mock_instance.messages.create.call_args
                assert call_kwargs[1]["model"] == "claude-opus-4"

    @pytest.mark.asyncio
    async def test_authentication_error(self, client: AnthropicMessagesClient) -> None:
        """Test authentication error handling."""
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

    @pytest.mark.asyncio
    async def test_streaming_request_success(self, client: AnthropicMessagesClient) -> None:
        """Test successful streaming request with stream key removal."""
        from unittest.mock import MagicMock

        # Create mock stream events
        mock_event = MagicMock()
        mock_event.type = "content_block_delta"
        mock_event.model_dump = MagicMock(
            return_value={
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "Hello"},
            }
        )

        # Create mock stream context manager
        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=None)
        mock_stream.__aiter__ = MagicMock(return_value=iter([mock_event]))

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                        "stream": True,  # This should be filtered out
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                # Collect chunks from the generator
                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                # Verify we got chunks
                assert len(chunks) > 0

                # Verify stream key was NOT passed to messages.stream()
                call_kwargs = mock_instance.messages.stream.call_args[1]
                assert "stream" not in call_kwargs

    @pytest.mark.asyncio
    async def test_streaming_request_model_injection(self, client: AnthropicMessagesClient) -> None:
        """Test model is injected during streaming request."""
        from unittest.mock import MagicMock

        mock_event = MagicMock()
        mock_event.type = "message_start"
        mock_event.model_dump = MagicMock(
            return_value={
                "type": "message_start",
                "message": {"id": "msg_123", "model": "claude-sonnet-4-20250514"},
            }
        )

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=None)
        mock_stream.__aiter__ = MagicMock(return_value=iter([mock_event]))

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                # Consume the generator
                async for _ in result:
                    pass

                # Check that model was injected
                call_kwargs = mock_instance.messages.stream.call_args[1]
                assert call_kwargs["model"] == "claude-sonnet-4-20250514"

    @pytest.mark.asyncio
    async def test_streaming_request_authentication_error(
        self, client: AnthropicMessagesClient
    ) -> None:
        """Test streaming request authentication error handling."""
        from unittest.mock import MagicMock

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(
            side_effect=AuthenticationError(
                message="Invalid API key",
                response=MagicMock(status_code=401),
                body={"error": {"message": "Invalid API key"}},
            )
        )
        mock_stream.__aexit__ = AsyncMock(return_value=None)

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                # Collect chunks from the generator
                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                # Should have error chunk
                assert len(chunks) == 1
                import json

                error_data = json.loads(chunks[0].replace("data: ", "").strip())
                assert "error" in error_data
                assert error_data["status_code"] == 401

    @pytest.mark.asyncio
    async def test_streaming_request_rate_limit_error(
        self, client: AnthropicMessagesClient
    ) -> None:
        """Test streaming request rate limit error handling."""
        from unittest.mock import MagicMock

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(
            side_effect=RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body={"error": {"message": "Rate limit exceeded"}},
            )
        )
        mock_stream.__aexit__ = AsyncMock(return_value=None)

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                assert len(chunks) == 1
                import json

                error_data = json.loads(chunks[0].replace("data: ", "").strip())
                assert "error" in error_data
                assert error_data["status_code"] == 429

    @pytest.mark.asyncio
    async def test_streaming_request_connection_error(
        self, client: AnthropicMessagesClient
    ) -> None:
        """Test streaming request connection error handling."""
        from unittest.mock import MagicMock

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(side_effect=APIConnectionError(request=MagicMock()))
        mock_stream.__aexit__ = AsyncMock(return_value=None)

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 1024,
                    },
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                assert len(chunks) == 1
                import json

                error_data = json.loads(chunks[0].replace("data: ", "").strip())
                assert "error" in error_data
                assert error_data["status_code"] == 500

    @pytest.mark.asyncio
    async def test_streaming_standard_events_passthrough(
        self, client: AnthropicMessagesClient
    ) -> None:
        """Test standard Anthropic events are passed through."""
        from unittest.mock import MagicMock

        # Create mock events for standard types with proper structure
        message_start_event = MagicMock()
        message_start_event.type = "message_start"
        message_start_event.model_dump = MagicMock(
            return_value={
                "type": "message_start",
                "message": {"id": "msg_123", "model": "claude-3"},
            }
        )

        content_block_delta_event = MagicMock()
        content_block_delta_event.type = "content_block_delta"
        content_block_delta_event.model_dump = MagicMock(
            return_value={
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "Hello"},
            }
        )

        message_stop_event = MagicMock()
        message_stop_event.type = "message_stop"
        message_stop_event.model_dump = MagicMock(return_value={"type": "message_stop"})

        events = [message_start_event, content_block_delta_event, message_stop_event]

        # Create async iterator helper
        async def async_iter():
            for event in events:
                yield event

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=None)
        mock_stream.__aiter__ = MagicMock(return_value=async_iter())

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 1024},
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                # Should have chunks for:
                # 1. message_start (initial chunk with role)
                # 2. content_block_delta (content chunk)
                # 3. message_stop ([DONE] marker)
                assert len(chunks) == 3
                # First chunk should have role
                assert '"role": "assistant"' in chunks[0]
                # Second chunk should have content
                assert '"content": "Hello"' in chunks[1]
                # Third chunk should be [DONE]
                assert chunks[2] == "data: [DONE]\n\n"

    @pytest.mark.asyncio
    async def test_streaming_text_event_filtered(self, client: AnthropicMessagesClient) -> None:
        """Test 'text' convenience events are filtered out."""
        from unittest.mock import MagicMock

        # Create standard event and non-standard 'text' event
        standard_event = MagicMock()
        standard_event.type = "content_block_delta"
        standard_event.model_dump = MagicMock(
            return_value={"type": "content_block_delta", "delta": {"text": "Hello"}}
        )

        text_event = MagicMock()
        text_event.type = "text"
        text_event.model_dump = MagicMock(
            return_value={"type": "text", "text": "Hello", "snapshot": "Hello"}
        )

        events = [standard_event, text_event, standard_event]

        # Create async iterator helper
        async def async_iter():
            for event in events:
                yield event

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=None)
        mock_stream.__aiter__ = MagicMock(return_value=async_iter())

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 1024},
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                # Should only have chunks for standard events (content_block_delta twice)
                # The 'text' event should be filtered out
                for chunk in chunks:
                    if chunk.startswith("event:"):
                        assert "event: text" not in chunk

    @pytest.mark.asyncio
    async def test_streaming_unknown_event_filtered(self, client: AnthropicMessagesClient) -> None:
        """Test unknown event types are filtered out."""
        from unittest.mock import MagicMock

        standard_event = MagicMock()
        standard_event.type = "content_block_delta"
        standard_event.model_dump = MagicMock(
            return_value={"type": "content_block_delta", "delta": {"text": "Hello"}}
        )

        unknown_event = MagicMock()
        unknown_event.type = "unknown_event_type"
        unknown_event.model_dump = MagicMock(
            return_value={"type": "unknown_event_type", "data": "test"}
        )

        events = [standard_event, unknown_event]

        # Create async iterator helper
        async def async_iter():
            for event in events:
                yield event

        mock_stream = AsyncMock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock(return_value=None)
        mock_stream.__aiter__ = MagicMock(return_value=async_iter())

        with patch("psi_agent.ai.anthropic_messages.client.AsyncAnthropic") as mock_anthropic:
            mock_instance = AsyncMock()
            mock_instance.messages.stream = MagicMock(return_value=mock_stream)
            mock_instance.close = AsyncMock()
            mock_anthropic.return_value = mock_instance

            async with client:
                result = await client.messages(
                    {"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 1024},
                    stream=True,
                )

                # Type narrowing: streaming returns AsyncGenerator
                assert isinstance(result, AsyncGenerator)

                chunks = []
                async for chunk in result:
                    chunks.append(chunk)

                # Should only have chunks for standard events
                for chunk in chunks:
                    if chunk.startswith("event:"):
                        assert "event: unknown_event_type" not in chunk
