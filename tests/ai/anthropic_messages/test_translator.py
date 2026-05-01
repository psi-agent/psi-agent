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

    def test_tools_translation_openai_format(self) -> None:
        """Test OpenAI tools format is translated to Anthropic format."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "bash",
                        "description": "Execute a bash command",
                        "parameters": {
                            "type": "object",
                            "properties": {"command": {"type": "string", "description": "Command"}},
                            "required": ["command"],
                        },
                    },
                }
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert "tools" in result
        assert len(result["tools"]) == 1
        tool = result["tools"][0]
        assert tool["name"] == "bash"
        assert tool["description"] == "Execute a bash command"
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"
        assert "parameters" not in tool
        assert "function" not in tool

    def test_tools_passthrough_anthropic_format(self) -> None:
        """Test tools already in Anthropic format are passed through."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "tools": [
                {
                    "name": "bash",
                    "description": "Execute a bash command",
                    "input_schema": {
                        "type": "object",
                        "properties": {"command": {"type": "string", "description": "Command"}},
                        "required": ["command"],
                    },
                }
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert "tools" in result
        assert result["tools"][0]["name"] == "bash"
        assert "input_schema" in result["tools"][0]

    def test_tools_without_description(self) -> None:
        """Test tools without description field."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "simple_tool",
                        "parameters": {"type": "object"},
                    },
                }
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert result["tools"][0]["name"] == "simple_tool"
        assert "description" not in result["tools"][0]

    def test_no_tools_parameter(self) -> None:
        """Test request without tools parameter."""
        openai_request = {
            "messages": [{"role": "user", "content": "Hello"}],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert "tools" not in result

    def test_tool_result_message_translation(self) -> None:
        """Test tool result message is translated to Anthropic format."""
        openai_request = {
            "messages": [
                {"role": "user", "content": "What is the date?"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {"name": "bash", "arguments": '{"command": "date"}'},
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_123",
                    "content": "Mon May  1 13:48:07 CST 2026",
                },
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assert len(result["messages"]) == 3
        # Check assistant message with tool_calls
        assistant_msg = result["messages"][1]
        assert assistant_msg["role"] == "assistant"
        assert len(assistant_msg["content"]) == 1
        assert assistant_msg["content"][0]["type"] == "tool_use"
        assert assistant_msg["content"][0]["id"] == "call_123"
        assert assistant_msg["content"][0]["name"] == "bash"
        assert assistant_msg["content"][0]["input"] == {"command": "date"}

        # Check tool result message
        tool_msg = result["messages"][2]
        assert tool_msg["role"] == "user"
        assert len(tool_msg["content"]) == 1
        assert tool_msg["content"][0]["type"] == "tool_result"
        assert tool_msg["content"][0]["tool_use_id"] == "call_123"
        assert tool_msg["content"][0]["content"] == "Mon May  1 13:48:07 CST 2026"

    def test_assistant_message_with_tool_calls_and_text(self) -> None:
        """Test assistant message with both text and tool_calls."""
        openai_request = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {
                    "role": "assistant",
                    "content": "Let me check that.",
                    "tool_calls": [
                        {
                            "id": "call_456",
                            "type": "function",
                            "function": {"name": "read", "arguments": '{"file": "test.txt"}'},
                        }
                    ],
                },
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        assistant_msg = result["messages"][1]
        assert assistant_msg["role"] == "assistant"
        # Should have text block and tool_use block
        assert len(assistant_msg["content"]) == 2
        # Find text block
        text_blocks = [b for b in assistant_msg["content"] if b.get("type") == "text"]
        assert len(text_blocks) == 1
        assert text_blocks[0]["text"] == "Let me check that."
        # Find tool_use block
        tool_blocks = [b for b in assistant_msg["content"] if b.get("type") == "tool_use"]
        assert len(tool_blocks) == 1
        assert tool_blocks[0]["name"] == "read"

    def test_tool_result_with_non_string_content(self) -> None:
        """Test tool result with non-string content is converted."""
        openai_request = {
            "messages": [
                {
                    "role": "tool",
                    "tool_call_id": "call_789",
                    "content": {"result": "success"},  # dict, not string
                },
            ],
        }

        result = translate_openai_to_anthropic(openai_request)

        tool_msg = result["messages"][0]
        assert tool_msg["role"] == "user"
        assert tool_msg["content"][0]["type"] == "tool_result"
        # Content should be converted to string
        assert "result" in tool_msg["content"][0]["content"]


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


class TestStreamingThinkingSupport:
    """Tests for thinking block streaming translation."""

    def test_thinking_block_start_no_output(self) -> None:
        """Test content_block_start with thinking type returns None."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_start",
            {
                "index": 0,
                "content_block": {
                    "type": "thinking",
                    "thinking": "",
                    "signature": "",
                },
            },
        )

        assert result is None

    def test_thinking_delta_produces_reasoning_content(self) -> None:
        """Test thinking_delta event produces reasoning_content chunk."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "thinking_delta",
                    "thinking": "Let me think about this...",
                },
            },
        )

        assert result is not None
        assert '"reasoning_content": "Let me think about this..."' in result

    def test_signature_delta_no_output(self) -> None:
        """Test signature_delta event produces no output."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "signature_delta",
                    "signature": "abc123",
                },
            },
        )

        assert result is None

    def test_redacted_thinking_block_start_skipped(self) -> None:
        """Test redacted_thinking block start is skipped and tracked."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_start",
            {
                "index": 0,
                "content_block": {
                    "type": "redacted_thinking",
                    "data": "encrypted",
                },
            },
        )

        assert result is None
        assert 0 in translator._redacted_indices

    def test_redacted_thinking_delta_skipped(self) -> None:
        """Test delta for redacted_thinking block is skipped."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"
        # Mark index 0 as redacted
        translator._redacted_indices.add(0)

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "thinking_delta",
                    "thinking": "should be skipped",
                },
            },
        )

        assert result is None

    def test_content_block_stop_clears_redacted_index(self) -> None:
        """Test content_block_stop clears redacted thinking index."""
        translator = StreamingTranslator()
        translator._redacted_indices.add(0)

        result = translator.translate_event(
            "content_block_stop",
            {"index": 0},
        )

        assert result is None
        assert 0 not in translator._redacted_indices

    def test_multiple_thinking_deltas(self) -> None:
        """Test multiple thinking_delta events produce separate chunks."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result1 = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "thinking_delta",
                    "thinking": "First thought",
                },
            },
        )

        result2 = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "thinking_delta",
                    "thinking": "Second thought",
                },
            },
        )

        assert result1 is not None
        assert result2 is not None
        assert '"reasoning_content": "First thought"' in result1
        assert '"reasoning_content": "Second thought"' in result2

    def test_text_delta_with_type_discriminator(self) -> None:
        """Test text_delta with proper type discriminator."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "text_delta",
                    "text": "Hello world",
                },
            },
        )

        assert result is not None
        assert '"content": "Hello world"' in result

    def test_empty_text_delta_no_output(self) -> None:
        """Test text_delta with empty text produces no output."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "text_delta",
                    "text": "",
                },
            },
        )

        assert result is None

    def test_empty_thinking_delta_no_output(self) -> None:
        """Test thinking_delta with empty thinking produces no output."""
        translator = StreamingTranslator()
        translator._message_id = "msg_123"
        translator._model = "claude-3"

        result = translator.translate_event(
            "content_block_delta",
            {
                "index": 0,
                "delta": {
                    "type": "thinking_delta",
                    "thinking": "",
                },
            },
        )

        assert result is None


class TestTranslateAnthropicStreamThinking:
    """Tests for async stream translation with thinking content."""

    async def test_stream_with_thinking_then_text(self) -> None:
        """Test full stream with thinking followed by text."""
        import json

        async def mock_stream() -> AsyncGenerator[str]:
            # message_start event
            msg_start = json.dumps({"message": {"id": "msg_123", "model": "claude-3"}})
            yield f"event: message_start\ndata: {msg_start}\n\n"
            # thinking block start
            thinking_start = json.dumps(
                {
                    "index": 0,
                    "content_block": {
                        "type": "thinking",
                        "thinking": "",
                        "signature": "",
                    },
                }
            )
            yield f"event: content_block_start\ndata: {thinking_start}\n\n"
            # thinking_delta
            thinking_delta = json.dumps(
                {
                    "index": 0,
                    "delta": {
                        "type": "thinking_delta",
                        "thinking": "Let me analyze this...",
                    },
                }
            )
            yield f"event: content_block_delta\ndata: {thinking_delta}\n\n"
            # signature_delta
            sig_delta = json.dumps(
                {
                    "index": 0,
                    "delta": {
                        "type": "signature_delta",
                        "signature": "sig123",
                    },
                }
            )
            yield f"event: content_block_delta\ndata: {sig_delta}\n\n"
            # thinking block stop
            yield 'event: content_block_stop\ndata: {"index": 0}\n\n'
            # text block start
            text_start = json.dumps(
                {
                    "index": 1,
                    "content_block": {
                        "type": "text",
                        "text": "",
                    },
                }
            )
            yield f"event: content_block_start\ndata: {text_start}\n\n"
            # text_delta
            text_delta = json.dumps(
                {
                    "index": 1,
                    "delta": {
                        "type": "text_delta",
                        "text": "The answer is 42.",
                    },
                }
            )
            yield f"event: content_block_delta\ndata: {text_delta}\n\n"
            # text block stop
            yield 'event: content_block_stop\ndata: {"index": 1}\n\n'
            # message_delta with end_turn
            msg_delta = json.dumps({"delta": {"stop_reason": "end_turn"}})
            yield f"event: message_delta\ndata: {msg_delta}\n\n"
            # message_stop event
            yield "event: message_stop\ndata: {}\n\n"

        chunks = []
        async for chunk in translate_anthropic_stream(mock_stream()):
            chunks.append(chunk)

        # Should have: message_start, thinking_delta, text_delta, message_delta, message_stop
        assert len(chunks) == 5
        # Check reasoning_content in thinking chunk
        assert '"reasoning_content": "Let me analyze this..."' in chunks[1]
        # Check content in text chunk
        assert '"content": "The answer is 42."' in chunks[2]
        # Check finish reason
        assert '"finish_reason": "stop"' in chunks[3]
        # Last chunk is [DONE]
        assert chunks[4] == "data: [DONE]\n\n"

    async def test_stream_with_tool_calls_and_thinking(self) -> None:
        """Test full stream with thinking and tool calls mixed."""
        import json

        async def mock_stream() -> AsyncGenerator[str]:
            # message_start event
            msg_start = json.dumps({"message": {"id": "msg_123", "model": "claude-3"}})
            yield f"event: message_start\ndata: {msg_start}\n\n"
            # thinking block start
            thinking_start = json.dumps(
                {
                    "index": 0,
                    "content_block": {
                        "type": "thinking",
                        "thinking": "",
                        "signature": "",
                    },
                }
            )
            yield f"event: content_block_start\ndata: {thinking_start}\n\n"
            # thinking_delta
            thinking_delta = json.dumps(
                {
                    "index": 0,
                    "delta": {
                        "type": "thinking_delta",
                        "thinking": "I need to use a tool...",
                    },
                }
            )
            yield f"event: content_block_delta\ndata: {thinking_delta}\n\n"
            # thinking block stop
            yield 'event: content_block_stop\ndata: {"index": 0}\n\n'
            # tool_use block start
            tool_start = json.dumps(
                {
                    "index": 1,
                    "content_block": {
                        "type": "tool_use",
                        "id": "toolu_123",
                        "name": "bash",
                        "input": {},
                    },
                }
            )
            yield f"event: content_block_start\ndata: {tool_start}\n\n"
            # input_json_delta
            tool_delta = json.dumps(
                {
                    "index": 1,
                    "delta": {
                        "type": "input_json_delta",
                        "partial_json": '{"command": "ls"}',
                    },
                }
            )
            yield f"event: content_block_delta\ndata: {tool_delta}\n\n"
            # tool block stop
            yield 'event: content_block_stop\ndata: {"index": 1}\n\n'
            # message_delta with tool_use stop_reason
            msg_delta = json.dumps({"delta": {"stop_reason": "tool_use"}})
            yield f"event: message_delta\ndata: {msg_delta}\n\n"
            # message_stop event
            yield "event: message_stop\ndata: {}\n\n"

        chunks = []
        async for chunk in translate_anthropic_stream(mock_stream()):
            chunks.append(chunk)

        # Should have: message_start, thinking_delta, tool_use start, input_json_delta,
        # message_delta, message_stop
        assert len(chunks) == 6
        # Check reasoning_content in thinking chunk
        assert '"reasoning_content": "I need to use a tool..."' in chunks[1]
        # Check tool_calls in third chunk
        assert '"tool_calls"' in chunks[2]
        assert '"bash"' in chunks[2]
        # Check arguments in fourth chunk
        assert '"arguments"' in chunks[3]
        # Check finish reason
        assert '"finish_reason": "tool_calls"' in chunks[4]
        # Last chunk is [DONE]
        assert chunks[5] == "data: [DONE]\n\n"
