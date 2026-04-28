"""Protocol translation between OpenAI and Anthropic message formats."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any


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

    # Convert messages
    anthropic_messages = []
    for msg in filtered_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Convert content to Anthropic format (array of content blocks)
        if isinstance(content, str):
            anthropic_content = [{"type": "text", "text": content}]
        elif isinstance(content, list):
            # Already in content block format, pass through
            anthropic_content = content
        else:
            anthropic_content = [{"type": "text", "text": str(content)}]

        anthropic_messages.append({"role": role, "content": anthropic_content})

    anthropic_request["messages"] = anthropic_messages

    # Pass through common parameters
    for param in ["model", "max_tokens", "temperature", "stream", "top_p", "stop"]:
        if param in openai_request:
            anthropic_request[param] = openai_request[param]

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

    def _make_chunk(self, content: str | None = None, finish_reason: str | None = None) -> str:
        """Create an OpenAI streaming chunk.

        Args:
            content: The content delta, if any.
            finish_reason: The finish reason, if any.

        Returns:
            SSE formatted chunk string.
        """
        delta: dict[str, Any] = {"role": "assistant"}
        if content is not None:
            delta["content"] = content

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
            # No output needed for content block start
            return None

        if event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            text = delta.get("text", "")
            if text:
                return self._make_chunk(content=text)
            return None

        if event_type == "content_block_stop":
            # No output needed for content block stop
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
