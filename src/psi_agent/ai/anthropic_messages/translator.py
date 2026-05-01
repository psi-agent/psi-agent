"""Protocol translation between OpenAI and Anthropic message formats."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

from loguru import logger


def _translate_tool_to_anthropic(openai_tool: dict[str, Any]) -> dict[str, Any]:
    """Translate a single OpenAI tool definition to Anthropic format.

    Args:
        openai_tool: OpenAI tool definition (may be OpenAI or Anthropic format).

    Returns:
        Anthropic tool definition.
    """
    # Check if already in Anthropic format (has input_schema)
    if "input_schema" in openai_tool:
        return openai_tool

    # OpenAI format: {"type": "function", "function": {...}}
    if openai_tool.get("type") == "function" and "function" in openai_tool:
        func = openai_tool["function"]
        anthropic_tool: dict[str, Any] = {
            "name": func.get("name", ""),
            "input_schema": func.get("parameters", {"type": "object"}),
        }
        if "description" in func:
            anthropic_tool["description"] = func["description"]
        return anthropic_tool

    # Unknown format - pass through as-is
    return openai_tool


def _translate_tools_to_anthropic(openai_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate OpenAI tools array to Anthropic format.

    Args:
        openai_tools: OpenAI tools array.

    Returns:
        Anthropic tools array.
    """
    return [_translate_tool_to_anthropic(tool) for tool in openai_tools]


def _translate_message_to_anthropic(msg: dict[str, Any]) -> dict[str, Any] | None:
    """Translate a single OpenAI message to Anthropic format.

    Args:
        msg: OpenAI message format.

    Returns:
        Anthropic message format, or None if system message (should be extracted separately).
    """
    role = msg.get("role", "user")
    content = msg.get("content", "")

    # Handle tool result message: role="tool" -> role="user" with tool_result block
    if role == "tool":
        tool_call_id = msg.get("tool_call_id", "")
        tool_content = msg.get("content", "")
        # Ensure content is string
        if not isinstance(tool_content, str):
            tool_content = str(tool_content) if tool_content is not None else ""
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": tool_content,
                }
            ],
        }

    # Handle assistant message with tool_calls
    if role == "assistant" and "tool_calls" in msg:
        tool_calls = msg.get("tool_calls", [])
        content_blocks: list[dict[str, Any]] = []

        # Add text content if present
        if content and isinstance(content, str) and content.strip():
            content_blocks.append({"type": "text", "text": content})

        # Add tool_use blocks
        for tc in tool_calls:
            tc_id = tc.get("id", "")
            tc_function = tc.get("function", {})
            tc_name = tc_function.get("name", "")
            tc_args = tc_function.get("arguments", "{}")

            # Parse arguments JSON string to object
            try:
                tc_input = json.loads(tc_args) if tc_args else {}
            except json.JSONDecodeError:
                tc_input = {}

            content_blocks.append(
                {
                    "type": "tool_use",
                    "id": tc_id,
                    "name": tc_name,
                    "input": tc_input,
                }
            )

        return {"role": "assistant", "content": content_blocks}

    # Standard message conversion
    if isinstance(content, str):
        anthropic_content = [{"type": "text", "text": content}]
    elif isinstance(content, list):
        # Already in content block format, pass through
        anthropic_content = content
    else:
        anthropic_content = [{"type": "text", "text": str(content)}]

    return {"role": role, "content": anthropic_content}


def translate_openai_to_anthropic(
    openai_request: dict[str, Any], max_tokens: int = 4096
) -> dict[str, Any]:
    """Translate OpenAI chat completions request to Anthropic Messages format.

    Args:
        openai_request: OpenAI chat completions request format.
        max_tokens: Default max_tokens to use if not provided in request.

    Returns:
        Anthropic Messages request format.
    """
    anthropic_request: dict[str, Any] = {}

    # Extract and remove system message if present
    messages = openai_request.get("messages", [])
    system_content = None
    filtered_messages = []

    for msg in messages:
        if msg.get("role") == "system" and system_content is None:
            # Extract first system message as system parameter
            content = msg.get("content", "")
            if isinstance(content, str):
                system_content = content
            elif isinstance(content, list):
                # Handle content blocks - extract text
                texts = [block.get("text", "") for block in content if block.get("type") == "text"]
                system_content = " ".join(texts)
        else:
            filtered_messages.append(msg)

    if system_content:
        anthropic_request["system"] = system_content

    # Convert messages using the translation helper
    anthropic_messages = []
    for msg in filtered_messages:
        translated = _translate_message_to_anthropic(msg)
        if translated is not None:
            anthropic_messages.append(translated)

    anthropic_request["messages"] = anthropic_messages

    # Translate tools from OpenAI format to Anthropic format
    if "tools" in openai_request:
        anthropic_request["tools"] = _translate_tools_to_anthropic(openai_request["tools"])

    # Pass through common parameters
    for param in ["model", "max_tokens", "temperature", "stream", "top_p", "stop"]:
        if param in openai_request:
            anthropic_request[param] = openai_request[param]

    # Pass through thinking toggle
    if "thinking" in openai_request:
        anthropic_request["thinking"] = openai_request["thinking"]

    # Map reasoning_effort to output_config.effort
    reasoning_effort = openai_request.get("reasoning_effort")
    if reasoning_effort is not None:
        anthropic_request["output_config"] = {"effort": reasoning_effort}

    # Add default max_tokens if not provided
    if "max_tokens" not in anthropic_request:
        anthropic_request["max_tokens"] = max_tokens

    return anthropic_request


def translate_anthropic_to_openai(anthropic_response: dict[str, Any]) -> dict[str, Any]:
    """Translate Anthropic Messages response to OpenAI chat completions format.

    Args:
        anthropic_response: Anthropic Messages response format.

    Returns:
        OpenAI chat completions response format.
    """
    # Extract text from content blocks
    content_blocks = anthropic_response.get("content", [])
    text_content = ""
    for block in content_blocks:
        if block.get("type") == "text":
            text_content += block.get("text", "")

    # Determine finish reason
    stop_reason = anthropic_response.get("stop_reason", "end_turn")
    finish_reason_map = {
        "end_turn": "stop",
        "max_tokens": "length",
        "stop_sequence": "stop",
        "tool_use": "tool_calls",
    }
    finish_reason = finish_reason_map.get(stop_reason, "stop")

    # Map usage statistics
    usage = anthropic_response.get("usage", {})
    openai_usage = {
        "prompt_tokens": usage.get("input_tokens", 0),
        "completion_tokens": usage.get("output_tokens", 0),
        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
    }

    # Construct OpenAI response
    return {
        "id": anthropic_response.get("id", ""),
        "object": "chat.completion",
        "created": 0,  # Anthropic doesn't provide this
        "model": anthropic_response.get("model", ""),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text_content},
                "finish_reason": finish_reason,
            }
        ],
        "usage": openai_usage,
    }


class StreamingTranslator:
    """Stateful translator for Anthropic streaming events to OpenAI chunks."""

    def __init__(self) -> None:
        """Initialize the streaming translator."""
        self._message_id: str = ""
        self._model: str = ""
        # Track pending tool calls by index: {index: {"id": str, "name": str}}
        self._pending_tool_calls: dict[int, dict[str, str]] = {}
        # Track redacted thinking blocks to skip (set of indices)
        self._redacted_indices: set[int] = set()

    def _make_chunk(
        self,
        content: str | None = None,
        finish_reason: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        reasoning_content: str | None = None,
    ) -> str:
        """Create an OpenAI streaming chunk.

        Args:
            content: The content delta, if any.
            finish_reason: The finish reason, if any.
            tool_calls: Tool calls delta, if any.
            reasoning_content: Reasoning content delta (for thinking blocks).

        Returns:
            SSE formatted chunk string.
        """
        delta: dict[str, Any] = {"role": "assistant"}
        if content is not None:
            delta["content"] = content
        if tool_calls is not None:
            delta["tool_calls"] = tool_calls
        if reasoning_content is not None:
            delta["reasoning_content"] = reasoning_content

        chunk = {
            "id": self._message_id,
            "object": "chat.completion.chunk",
            "created": 0,
            "model": self._model,
            "choices": [
                {
                    "index": 0,
                    "delta": delta,
                    "finish_reason": finish_reason,
                }
            ],
        }
        return f"data: {json.dumps(chunk)}\n\n"

    def translate_event(self, event_type: str, event_data: dict[str, Any]) -> str | None:
        """Translate a single Anthropic streaming event to OpenAI chunk.

        Args:
            event_type: The Anthropic event type.
            event_data: The event data dict.

        Returns:
            OpenAI SSE chunk string, or None if no output for this event.
        """
        if event_type == "message_start":
            message = event_data.get("message", {})
            self._message_id = message.get("id", "")
            self._model = message.get("model", "")
            # Emit initial chunk with role
            return self._make_chunk()

        if event_type == "content_block_start":
            content_block = event_data.get("content_block", {})
            block_type = content_block.get("type", "")
            index = event_data.get("index", 0)

            if block_type == "tool_use":
                tool_id = content_block.get("id", "")
                tool_name = content_block.get("name", "")
                self._pending_tool_calls[index] = {"id": tool_id, "name": tool_name}
                # Emit tool_calls chunk with id and name
                return self._make_chunk(
                    tool_calls=[
                        {
                            "index": index,
                            "id": tool_id,
                            "type": "function",
                            "function": {"name": tool_name, "arguments": ""},
                        }
                    ]
                )

            if block_type == "thinking":
                # No output needed for thinking block start
                return None

            if block_type == "redacted_thinking":
                # Track this index to skip all deltas for it
                self._redacted_indices.add(index)
                logger.debug(f"Skipping redacted_thinking block at index {index}")
                return None

            # Default: text block or other - no output needed
            return None

        if event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            index = event_data.get("index", 0)
            delta_type = delta.get("type", "")

            # Skip deltas for redacted thinking blocks
            if index in self._redacted_indices:
                return None

            # Handle thinking_delta - emit reasoning_content
            if delta_type == "thinking_delta":
                thinking = delta.get("thinking", "")
                if thinking:
                    return self._make_chunk(reasoning_content=thinking)
                return None

            # Handle signature_delta - no output (metadata only)
            if delta_type == "signature_delta":
                return None

            # Handle text_delta - emit content
            if delta_type == "text_delta":
                text = delta.get("text", "")
                if text:
                    return self._make_chunk(content=text)
                return None

            # Handle input_json_delta for tool calls
            if delta_type == "input_json_delta":
                partial_json = delta.get("partial_json", "")
                if partial_json and index in self._pending_tool_calls:
                    return self._make_chunk(
                        tool_calls=[
                            {
                                "index": index,
                                "function": {"arguments": partial_json},
                            }
                        ]
                    )
                return None

            # Backward compatibility: handle raw JSON events without type discriminator
            text = delta.get("text")
            if text:
                return self._make_chunk(content=text)

            return None

        if event_type == "content_block_stop":
            # Clean up pending tool call if any
            index = event_data.get("index", 0)
            if index in self._pending_tool_calls:
                del self._pending_tool_calls[index]
            # Clean up redacted thinking index if any
            self._redacted_indices.discard(index)
            return None

        if event_type == "message_delta":
            # May contain stop_reason
            delta = event_data.get("delta", {})
            stop_reason = delta.get("stop_reason")
            if stop_reason:
                finish_reason_map = {
                    "end_turn": "stop",
                    "max_tokens": "length",
                    "stop_sequence": "stop",
                    "tool_use": "tool_calls",
                }
                finish_reason = finish_reason_map.get(stop_reason, "stop")
                return self._make_chunk(finish_reason=finish_reason)
            return None

        if event_type == "message_stop":
            # Emit [DONE] marker
            return "data: [DONE]\n\n"

        # Ignore other event types
        return None


async def translate_anthropic_stream(
    anthropic_stream: AsyncGenerator[str],
) -> AsyncGenerator[str]:
    """Translate Anthropic SSE stream to OpenAI chunk stream.

    Args:
        anthropic_stream: Async generator of Anthropic SSE event strings.

    Yields:
        OpenAI SSE chunk strings.
    """
    translator = StreamingTranslator()

    async for sse_event in anthropic_stream:
        # Parse SSE format: "event: <type>\ndata: <json>\n\n"
        lines = sse_event.strip().split("\n")
        event_type = ""
        event_data: dict[str, Any] = {}

        for line in lines:
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_str = line[5:].strip()
                try:
                    event_data = json.loads(data_str)
                except json.JSONDecodeError:
                    event_data = {}

        if event_type:
            chunk = translator.translate_event(event_type, event_data)
            if chunk:
                yield chunk
