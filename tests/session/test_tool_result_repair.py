"""Tests for tool result pairing repair functions."""

from __future__ import annotations


def _extract_tool_calls_from_assistant(message: dict) -> list[dict]:
    """Extract tool calls from an assistant message."""
    tool_calls: list[dict] = []

    # Check for OpenAI format: message.tool_calls
    if "tool_calls" in message and isinstance(message["tool_calls"], list):
        for tc in message["tool_calls"]:
            if isinstance(tc, dict):
                tool_call_id = tc.get("id", "")
                func = tc.get("function", {})
                name = func.get("name", "") if isinstance(func, dict) else ""
                if tool_call_id:
                    tool_calls.append({"id": tool_call_id, "name": name})

    # Check for Anthropic format: content blocks with type "tool_use"
    content = message.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") in ("tool_use", "toolCall"):
                tool_call_id = block.get("id", "")
                name = block.get("name", "")
                if tool_call_id:
                    tool_calls.append({"id": tool_call_id, "name": name})

    return tool_calls


def _extract_tool_result_id(message: dict) -> str | None:
    """Extract tool call ID from a tool result message."""
    # OpenAI format
    if "tool_call_id" in message:
        return str(message["tool_call_id"])

    # Anthropic format
    if "toolCallId" in message:
        return str(message["toolCallId"])

    return None


class ToolUseRepairReport:
    """Report from tool_use/tool_result pairing repair."""

    def __init__(self) -> None:
        self.messages: list[dict] = []
        self.dropped_orphan_count: int = 0
        self.dropped_duplicate_count: int = 0


def _repair_tool_use_result_pairing(messages: list[dict]) -> ToolUseRepairReport:
    """Repair tool_use/tool_result pairing in conversation history."""
    report = ToolUseRepairReport()
    out: list[dict] = []
    seen_tool_result_ids: set[str] = set()

    # Track all tool call IDs from assistant messages
    all_tool_call_ids: set[str] = set()
    for msg in messages:
        if msg.get("role") == "assistant":
            tool_calls = _extract_tool_calls_from_assistant(msg)
            for tc in tool_calls:
                all_tool_call_ids.add(tc["id"])

    # Second pass: filter messages
    for msg in messages:
        role = msg.get("role")

        if role == "tool" or role == "toolResult" or role == "tool_result":
            tool_call_id = _extract_tool_result_id(msg)

            if tool_call_id is None:
                out.append(msg)
            elif tool_call_id not in all_tool_call_ids:
                report.dropped_orphan_count += 1
            elif tool_call_id in seen_tool_result_ids:
                report.dropped_duplicate_count += 1
            else:
                seen_tool_result_ids.add(tool_call_id)
                out.append(msg)
        else:
            out.append(msg)

    report.messages = out
    return report


class TestExtractToolCallsFromAssistant:
    """Tests for _extract_tool_calls_from_assistant."""

    def test_openai_format(self) -> None:
        """Test extraction from OpenAI format."""
        message = {
            "role": "assistant",
            "tool_calls": [
                {"id": "call_123", "function": {"name": "read", "arguments": "{}"}},
                {"id": "call_456", "function": {"name": "write", "arguments": "{}"}},
            ],
        }
        result = _extract_tool_calls_from_assistant(message)
        assert len(result) == 2
        assert result[0] == {"id": "call_123", "name": "read"}
        assert result[1] == {"id": "call_456", "name": "write"}

    def test_anthropic_format(self) -> None:
        """Test extraction from Anthropic format."""
        message = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Let me read the file."},
                {"type": "tool_use", "id": "toolu_123", "name": "read", "input": {}},
            ],
        }
        result = _extract_tool_calls_from_assistant(message)
        assert len(result) == 1
        assert result[0] == {"id": "toolu_123", "name": "read"}

    def test_no_tool_calls(self) -> None:
        """Test message with no tool calls."""
        message = {"role": "assistant", "content": "Hello!"}
        result = _extract_tool_calls_from_assistant(message)
        assert len(result) == 0

    def test_mixed_formats(self) -> None:
        """Test message with both OpenAI and Anthropic tool calls."""
        message = {
            "role": "assistant",
            "tool_calls": [{"id": "call_123", "function": {"name": "read"}}],
            "content": [{"type": "tool_use", "id": "toolu_456", "name": "write"}],
        }
        result = _extract_tool_calls_from_assistant(message)
        assert len(result) == 2


class TestExtractToolResultId:
    """Tests for _extract_tool_result_id."""

    def test_openai_format(self) -> None:
        """Test extraction from OpenAI format."""
        message = {"role": "tool", "tool_call_id": "call_123", "content": "result"}
        result = _extract_tool_result_id(message)
        assert result == "call_123"

    def test_anthropic_format(self) -> None:
        """Test extraction from Anthropic format."""
        message = {
            "role": "toolResult",
            "toolCallId": "toolu_123",
            "content": "result",
        }
        result = _extract_tool_result_id(message)
        assert result == "toolu_123"

    def test_no_id(self) -> None:
        """Test message with no tool call ID."""
        message = {"role": "tool", "content": "result"}
        result = _extract_tool_result_id(message)
        assert result is None


class TestRepairToolUseResultPairing:
    """Tests for _repair_tool_use_result_pairing."""

    def test_no_repair_needed(self) -> None:
        """Test history that doesn't need repair."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
        report = _repair_tool_use_result_pairing(messages)
        assert len(report.messages) == 2
        assert report.dropped_orphan_count == 0
        assert report.dropped_duplicate_count == 0

    def test_orphaned_tool_result_removed(self) -> None:
        """Test that orphaned tool results are removed."""
        messages = [
            {"role": "user", "content": "Read file"},
            {"role": "assistant", "content": "Done"},
            {"role": "tool", "tool_call_id": "call_123", "content": "file content"},
        ]
        report = _repair_tool_use_result_pairing(messages)
        assert len(report.messages) == 2
        assert report.dropped_orphan_count == 1
        assert report.dropped_duplicate_count == 0

    def test_matched_tool_result_kept(self) -> None:
        """Test that matched tool results are kept."""
        messages = [
            {"role": "user", "content": "Read file"},
            {
                "role": "assistant",
                "tool_calls": [{"id": "call_123", "function": {"name": "read"}}],
            },
            {"role": "tool", "tool_call_id": "call_123", "content": "file content"},
        ]
        report = _repair_tool_use_result_pairing(messages)
        assert len(report.messages) == 3
        assert report.dropped_orphan_count == 0
        assert report.dropped_duplicate_count == 0

    def test_duplicate_tool_result_removed(self) -> None:
        """Test that duplicate tool results are removed."""
        messages = [
            {"role": "user", "content": "Read file"},
            {
                "role": "assistant",
                "tool_calls": [{"id": "call_123", "function": {"name": "read"}}],
            },
            {"role": "tool", "tool_call_id": "call_123", "content": "result 1"},
            {"role": "tool", "tool_call_id": "call_123", "content": "result 2"},
        ]
        report = _repair_tool_use_result_pairing(messages)
        assert len(report.messages) == 3
        assert report.dropped_orphan_count == 0
        assert report.dropped_duplicate_count == 1

    def test_multiple_orphans(self) -> None:
        """Test multiple orphaned tool results."""
        messages = [
            {"role": "user", "content": "Read files"},
            {"role": "assistant", "content": "Done"},
            {"role": "tool", "tool_call_id": "call_123", "content": "file 1"},
            {"role": "tool", "tool_call_id": "call_456", "content": "file 2"},
        ]
        report = _repair_tool_use_result_pairing(messages)
        assert len(report.messages) == 2
        assert report.dropped_orphan_count == 2

    def test_partial_match(self) -> None:
        """Test history with some matched and some orphaned results."""
        messages = [
            {"role": "user", "content": "Read files"},
            {
                "role": "assistant",
                "tool_calls": [{"id": "call_123", "function": {"name": "read"}}],
            },
            {"role": "tool", "tool_call_id": "call_123", "content": "file 1"},
            {"role": "tool", "tool_call_id": "call_456", "content": "file 2"},
        ]
        report = _repair_tool_use_result_pairing(messages)
        assert len(report.messages) == 3
        assert report.dropped_orphan_count == 1
