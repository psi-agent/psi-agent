"""Tests for protocol translation between OpenAI and Anthropic formats."""

from __future__ import annotations

from psi_agent.ai.anthropic_messages.translator import (
    translate_anthropic_to_openai,
    translate_openai_to_anthropic,
)


class TestTranslateOpenAIToAnthropic:
    """Tests for OpenAI to Anthropic request translation."""

    def test_basic_text_message(self) -> None:
        """Test basic text message translation."""
        openai_request = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Hello, world!"},
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["messages"] == [
            {"role": "user", "content": [{"type": "text", "text": "Hello, world!"}]},
        ]
        assert result["model"] == "gpt-4"

    def test_system_message_extraction(self) -> None:
        """Test system message is extracted as system parameter."""
        openai_request = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["system"] == "You are a helpful assistant."
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"

    def test_multiple_messages(self) -> None:
        """Test multiple messages are translated correctly."""
        openai_request = {
            "messages": [
                {"role": "system", "content": "Be helpful."},
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello!"},
                {"role": "user", "content": "How are you?"},
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["system"] == "Be helpful."
        assert len(result["messages"]) == 3
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][1]["role"] == "assistant"
        assert result["messages"][2]["role"] == "user"

    def test_parameter_passthrough(self) -> None:
        """Test common parameters are passed through."""
        openai_request = {
            "model": "claude-3",
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": True,
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["model"] == "claude-3"
        assert result["max_tokens"] == 100
        assert result["temperature"] == 0.7
        assert result["stream"] is True

    def test_content_block_passthrough(self) -> None:
        """Test content blocks are passed through unchanged."""
        openai_request = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello"}],
                },
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["messages"][0]["content"] == [{"type": "text", "text": "Hello"}]

    def test_default_max_tokens(self) -> None:
        """Test default max_tokens is added when not provided."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["max_tokens"] == 4096

    def test_custom_max_tokens_default(self) -> None:
        """Test custom max_tokens default is used when not provided."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
        }

        result = translate_openai_to_anthropic(openai_request, max_tokens=8192)

        assert result["max_tokens"] == 8192

    def test_max_tokens_not_overridden(self) -> None:
        """Test max_tokens is not overridden when provided in request."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 2048,
        }

        result = translate_openai_to_anthropic(openai_request, max_tokens=8192)

        assert result["max_tokens"] == 2048


class TestTranslateAnthropicToOpenAI:
    """Tests for Anthropic to OpenAI response translation."""

    def test_basic_response(self) -> None:
        """Test basic response translation."""
        anthropic_response = {
            "id": "msg_123",
            "model": "claude-3",
            "content": [{"type": "text", "text": "Hello, world!"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

        result = translate_anthropic_to_openai(anthropic_response)

        assert result["id"] == "msg_123"
        assert result["object"] == "chat.completion"
        assert result["model"] == "claude-3"
        assert len(result["choices"]) == 1
        assert result["choices"][0]["message"]["content"] == "Hello, world!"
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert result["choices"][0]["finish_reason"] == "stop"

    def test_usage_mapping(self) -> None:
        """Test usage statistics mapping."""
        anthropic_response = {
            "id": "msg_123",
            "content": [{"type": "text", "text": "Response"}],
            "usage": {"input_tokens": 100, "output_tokens": 50},
        }

        result = translate_anthropic_to_openai(anthropic_response)

        assert result["usage"]["prompt_tokens"] == 100
        assert result["usage"]["completion_tokens"] == 50
        assert result["usage"]["total_tokens"] == 150

    def test_finish_reason_mapping(self) -> None:
        """Test finish reason mapping."""
        test_cases = [
            ("end_turn", "stop"),
            ("max_tokens", "length"),
            ("stop_sequence", "stop"),
            ("tool_use", "tool_calls"),
        ]

        for stop_reason, expected_finish in test_cases:
            anthropic_response = {
                "id": "msg_123",
                "content": [{"type": "text", "text": "Response"}],
                "stop_reason": stop_reason,
            }

            result = translate_anthropic_to_openai(anthropic_response)
            assert result["choices"][0]["finish_reason"] == expected_finish

    def test_multiple_content_blocks(self) -> None:
        """Test multiple content blocks are concatenated."""
        anthropic_response = {
            "id": "msg_123",
            "content": [
                {"type": "text", "text": "Hello "},
                {"type": "text", "text": "world!"},
            ],
        }

        result = translate_anthropic_to_openai(anthropic_response)

        assert result["choices"][0]["message"]["content"] == "Hello world!"


class TestStreamingTranslator:
    """Tests for streaming event translation."""

    def test_message_start_event(self) -> None:
        """Test message_start event extracts id and model."""
        from psi_agent.ai.anthropic_messages.translator import StreamingTranslator

        translator = StreamingTranslator()
        result = translator.translate_event(
            "message_start",
            {"message": {"id": "msg_123", "model": "claude-3"}},
        )

        assert result is not None
        assert '"id": "msg_123"' in result
        assert '"model": "claude-3"' in result
        assert '"role": "assistant"' in result

    def test_content_block_delta_event(self) -> None:
        """Test content_block_delta event produces content chunk."""
        from psi_agent.ai.anthropic_messages.translator import StreamingTranslator

        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {"delta": {"text": "Hello"}},
        )

        assert result is not None
        assert '"content": "Hello"' in result

    def test_message_stop_event(self) -> None:
        """Test message_stop event produces [DONE] marker."""
        from psi_agent.ai.anthropic_messages.translator import StreamingTranslator

        translator = StreamingTranslator()

        result = translator.translate_event("message_stop", {})

        assert result == "data: [DONE]\n\n"

    def test_message_delta_with_stop_reason(self) -> None:
        """Test message_delta with stop_reason produces finish_reason."""
        from psi_agent.ai.anthropic_messages.translator import StreamingTranslator

        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "message_delta",
            {"delta": {"stop_reason": "end_turn"}},
        )

        assert result is not None
        assert '"finish_reason": "stop"' in result

    def test_ignored_events(self) -> None:
        """Test that some events produce no output."""
        from psi_agent.ai.anthropic_messages.translator import StreamingTranslator

        translator = StreamingTranslator()

        assert translator.translate_event("content_block_start", {}) is None
        assert translator.translate_event("content_block_stop", {}) is None
