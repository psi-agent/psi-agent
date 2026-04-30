"""Tests for protocol translation between OpenAI and Anthropic formats."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from psi_agent.ai.anthropic_messages.translator import (
    StreamingTranslator,
    translate_anthropic_stream,
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
        translator = StreamingTranslator()

        result = translator.translate_event("message_stop", {})

        assert result == "data: [DONE]\n\n"

    def test_message_delta_with_stop_reason(self) -> None:
        """Test message_delta with stop_reason produces finish_reason."""
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
        translator = StreamingTranslator()

        assert translator.translate_event("content_block_start", {}) is None
        assert translator.translate_event("content_block_stop", {}) is None

    def test_content_block_delta_empty_text(self) -> None:
        """Test content_block_delta with empty text produces no output."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {"delta": {"text": ""}},
        )

        assert result is None

    def test_message_delta_without_stop_reason(self) -> None:
        """Test message_delta without stop_reason produces no output."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "message_delta",
            {"delta": {}},
        )

        assert result is None

    def test_unknown_event_type(self) -> None:
        """Test unknown event type produces no output."""
        translator = StreamingTranslator()

        result = translator.translate_event("unknown_event", {})

        assert result is None


class TestTranslateOpenAIToAnthropicEdgeCases:
    """Tests for edge cases in OpenAI to Anthropic translation."""

    def test_system_message_with_content_blocks(self) -> None:
        """Test system message with content blocks is extracted correctly."""
        openai_request = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "You are "},
                        {"type": "text", "text": "helpful."},
                    ],
                },
                {"role": "user", "content": "Hello!"},
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["system"] == "You are  helpful."
        assert len(result["messages"]) == 1

    def test_non_string_non_list_content(self) -> None:
        """Test non-string, non-list content is converted to string."""
        openai_request = {
            "messages": [
                {"role": "user", "content": 12345},
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["messages"][0]["content"] == [{"type": "text", "text": "12345"}]

    def test_empty_messages(self) -> None:
        """Test empty messages list."""
        openai_request = {"messages": []}

        result = translate_openai_to_anthropic(openai_request)

        assert result["messages"] == []
        assert result["max_tokens"] == 4096

    def test_message_without_content(self) -> None:
        """Test message without content field."""
        openai_request = {
            "messages": [{"role": "user"}],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["messages"][0]["content"] == [{"type": "text", "text": ""}]

    def test_only_system_message(self) -> None:
        """Test request with only system message."""
        openai_request = {
            "messages": [{"role": "system", "content": "System prompt"}],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["system"] == "System prompt"
        assert result["messages"] == []


class TestTranslateAnthropicStream:
    """Tests for async stream translation."""

    async def test_stream_translation(self) -> None:
        """Test full stream translation."""
        import json

        async def mock_stream() -> AsyncGenerator[str]:
            # message_start event
            msg_start = json.dumps({"message": {"id": "msg_123", "model": "claude-3"}})
            yield f"event: message_start\ndata: {msg_start}\n\n"
            # content_block_delta event
            delta = json.dumps({"delta": {"text": "Hello"}})
            yield f"event: content_block_delta\ndata: {delta}\n\n"
            # message_stop event
            yield "event: message_stop\ndata: {}\n\n"

        chunks = []
        async for chunk in translate_anthropic_stream(mock_stream()):
            chunks.append(chunk)

        assert len(chunks) == 3  # message_start, content_block_delta, message_stop
        assert '"id": "msg_123"' in chunks[0]
        assert '"content": "Hello"' in chunks[1]
        assert chunks[2] == "data: [DONE]\n\n"

    async def test_stream_with_invalid_json(self) -> None:
        """Test stream handles invalid JSON gracefully."""

        async def mock_stream() -> AsyncGenerator[str]:
            yield "event: message_start\ndata: invalid json\n\n"

        chunks = []
        async for chunk in translate_anthropic_stream(mock_stream()):
            chunks.append(chunk)

        # Should produce initial chunk even with invalid JSON data
        assert len(chunks) == 1

    async def test_stream_with_message_delta_stop_reason(self) -> None:
        """Test stream with message_delta containing stop_reason."""
        import json

        async def mock_stream() -> AsyncGenerator[str]:
            msg_start = json.dumps({"message": {"id": "msg_123", "model": "claude-3"}})
            yield f"event: message_start\ndata: {msg_start}\n\n"
            delta = json.dumps({"delta": {"stop_reason": "end_turn"}})
            yield f"event: message_delta\ndata: {delta}\n\n"
            yield "event: message_stop\ndata: {}\n\n"

        chunks = []
        async for chunk in translate_anthropic_stream(mock_stream()):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert '"finish_reason": "stop"' in chunks[1]


class TestReasoningEffortTranslation:
    """Tests for reasoning_effort to output_config.effort translation."""

    def test_reasoning_effort_mapped_to_output_config(self) -> None:
        """Test reasoning_effort maps to output_config.effort."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "reasoning_effort": "high",
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["output_config"] == {"effort": "high"}

    def test_no_reasoning_effort(self) -> None:
        """Test no output_config when reasoning_effort is absent."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert "output_config" not in result

    def test_thinking_toggle_passed_through(self) -> None:
        """Test thinking toggle is passed through unchanged."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "thinking": {"type": "enabled"},
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["thinking"] == {"type": "enabled"}

    def test_thinking_disabled(self) -> None:
        """Test thinking disabled is passed through."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "thinking": {"type": "disabled"},
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["thinking"] == {"type": "disabled"}

    def test_both_thinking_and_reasoning_effort(self) -> None:
        """Test both thinking and reasoning_effort are handled."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "thinking": {"type": "enabled"},
            "reasoning_effort": "medium",
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["thinking"] == {"type": "enabled"}
        assert result["output_config"] == {"effort": "medium"}


class TestStreamingToolCalls:
    """Tests for streaming tool call translation."""

    def test_content_block_start_tool_use(self) -> None:
        """Test content_block_start with tool_use type produces tool_calls chunk."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_start",
            {
                "index": 0,
                "content_block": {
                    "type": "tool_use",
                    "id": "toolu_123",
                    "name": "bash",
                    "input": {},
                },
            },
        )

        assert result is not None
        assert '"tool_calls"' in result
        assert '"toolu_123"' in result
        assert '"bash"' in result
        # Verify pending tool call is tracked
        assert 0 in translator._pending_tool_calls
        assert translator._pending_tool_calls[0]["id"] == "toolu_123"

    def test_content_block_start_text_returns_none(self) -> None:
        """Test content_block_start with text type returns None."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_start",
            {
                "index": 0,
                "content_block": {
                    "type": "text",
                    "text": "",
                },
            },
        )

        assert result is None

    def test_content_block_delta_input_json_delta(self) -> None:
        """Test content_block_delta with input_json_delta produces tool_calls chunk."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"
        # Set up pending tool call
        translator._pending_tool_calls[0] = {"id": "toolu_123", "name": "bash"}

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "input_json_delta",
                    "partial_json": '{"command": "hostname"',
                },
            },
        )

        assert result is not None
        assert '"tool_calls"' in result
        assert '"arguments"' in result
        # Check that the partial_json is in the result (escaped in JSON)
        assert "hostname" in result

    def test_content_block_delta_input_json_delta_no_pending_tool(self) -> None:
        """Test input_json_delta without pending tool call returns None."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "input_json_delta",
                    "partial_json": '{"command": "hostname"',
                },
            },
        )

        assert result is None

    def test_content_block_delta_text_still_works(self) -> None:
        """Test content_block_delta with text still produces content chunk."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "text_delta",
                    "text": "Hello",
                },
            },
        )

        assert result is not None
        assert '"content": "Hello"' in result
        assert '"tool_calls"' not in result

    def test_content_block_stop_clears_pending_tool(self) -> None:
        """Test content_block_stop clears pending tool call."""
        translator = StreamingTranslator()
        translator._pending_tool_calls[0] = {"id": "toolu_123", "name": "bash"}

        result = translator.translate_event(
            "content_block_stop",
            {"index": 0},
        )

        assert result is None
        assert 0 not in translator._pending_tool_calls

    def test_message_delta_tool_use_finish_reason(self) -> None:
        """Test message_delta with tool_use stop_reason produces tool_calls finish."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "message_delta",
            {"delta": {"stop_reason": "tool_use"}},
        )

        assert result is not None
        assert '"finish_reason": "tool_calls"' in result


class TestTranslateAnthropicStreamToolCalls:
    """Tests for async stream translation with tool calls."""

    async def test_stream_tool_call_translation(self) -> None:
        """Test full stream translation with tool calls."""
        import json

        async def mock_stream() -> AsyncGenerator[str]:
            # message_start event
            msg_start = json.dumps({"message": {"id": "msg_123", "model": "claude-3"}})
            yield f"event: message_start\ndata: {msg_start}\n\n"
            # content_block_start for tool_use
            tool_start = json.dumps(
                {
                    "index": 0,
                    "content_block": {
                        "type": "tool_use",
                        "id": "toolu_123",
                        "name": "bash",
                        "input": {},
                    },
                }
            )
            yield f"event: content_block_start\ndata: {tool_start}\n\n"
            # content_block_delta with input_json_delta
            tool_delta = json.dumps(
                {
                    "index": 0,
                    "delta": {
                        "type": "input_json_delta",
                        "partial_json": '{"command": "hostname"}',
                    },
                }
            )
            yield f"event: content_block_delta\ndata: {tool_delta}\n\n"
            # content_block_stop
            yield 'event: content_block_stop\ndata: {"index": 0}\n\n'
            # message_delta with tool_use stop_reason
            msg_delta = json.dumps({"delta": {"stop_reason": "tool_use"}})
            yield f"event: message_delta\ndata: {msg_delta}\n\n"
            # message_stop event
            yield "event: message_stop\ndata: {}\n\n"

        chunks = []
        async for chunk in translate_anthropic_stream(mock_stream()):
            chunks.append(chunk)

        # Should have: message_start, tool_use start, input_json_delta, message_delta, message_stop
        assert len(chunks) == 5
        # Check tool_calls in second chunk
        assert '"tool_calls"' in chunks[1]
        assert '"bash"' in chunks[1]
        # Check arguments in third chunk
        assert '"arguments"' in chunks[2]
        # Check finish reason
        assert '"finish_reason": "tool_calls"' in chunks[3]
        # Last chunk is [DONE]
        assert chunks[4] == "data: [DONE]\n\n"
