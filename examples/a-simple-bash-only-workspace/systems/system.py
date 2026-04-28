"""Async system configuration for the workspace."""

import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

# Type aliases
CompleteFn = Callable[[list[dict[str, Any]]], Awaitable[str]]

# Type for extracted tool call
ToolCall = dict[str, Any]


def _extract_tool_calls_from_assistant(message: dict[str, Any]) -> list[ToolCall]:
    """Extract tool calls from an assistant message.

    Handles both OpenAI format (tool_calls) and Anthropic format (content blocks).

    Args:
        message: An assistant message dict.

    Returns:
        List of tool call dicts with 'id' and 'name' fields.
    """
    tool_calls: list[ToolCall] = []

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


def _extract_tool_result_id(message: dict[str, Any]) -> str | None:
    """Extract tool call ID from a tool result message.

    Handles both OpenAI format (tool_call_id) and Anthropic format (toolCallId).

    Args:
        message: A tool result message dict.

    Returns:
        Tool call ID string, or None if not found.
    """
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
        """Initialize the repair report."""
        self.messages: list[dict[str, Any]] = []
        self.dropped_orphan_count: int = 0
        self.dropped_duplicate_count: int = 0


def _repair_tool_use_result_pairing(
    messages: list[dict[str, Any]],
) -> ToolUseRepairReport:
    """Repair tool_use/tool_result pairing in conversation history.

    This function ensures that every tool_result has a corresponding tool_use.
    Orphaned tool results (no matching tool_use) and duplicate tool results
    are removed to prevent API errors.

    Args:
        messages: List of conversation messages to repair.

    Returns:
        ToolUseRepairReport with repaired messages and statistics.
    """
    report = ToolUseRepairReport()
    out: list[dict[str, Any]] = []
    seen_tool_result_ids: set[str] = set()

    # Track all tool call IDs from assistant messages
    all_tool_call_ids: set[str] = set()

    # First pass: collect all tool call IDs
    for msg in messages:
        if msg.get("role") == "assistant":
            tool_calls = _extract_tool_calls_from_assistant(msg)
            for tc in tool_calls:
                all_tool_call_ids.add(tc["id"])

    # Second pass: filter messages
    for msg in messages:
        role = msg.get("role")

        if role == "tool" or role == "toolResult" or role == "tool_result":
            # This is a tool result message
            tool_call_id = _extract_tool_result_id(msg)

            if tool_call_id is None:
                # No ID - keep it (might be a special case)
                out.append(msg)
            elif tool_call_id not in all_tool_call_ids:
                # Orphaned tool result - no matching tool_use
                report.dropped_orphan_count += 1
            elif tool_call_id in seen_tool_result_ids:
                # Duplicate tool result
                report.dropped_duplicate_count += 1
            else:
                # Valid tool result
                seen_tool_result_ids.add(tool_call_id)
                out.append(msg)
        else:
            # Non-tool-result messages are always kept
            out.append(msg)

    report.messages = out
    return report


async def _parse_skill_description(skill_md_path: Path) -> str | None:
    """Parse SKILL.md to extract description from YAML frontmatter.

    Args:
        skill_md_path: Path to the SKILL.md file.

    Returns:
        Description string if found, None otherwise.
    """
    content = skill_md_path.read_text()

    # Match YAML frontmatter between --- markers
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        return None

    frontmatter = frontmatter_match.group(1)

    # Extract description field
    description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if description_match:
        return description_match.group(1).strip()

    return None


def _estimate_tokens(message: dict[str, Any]) -> int:
    """Estimate token count for a message using chars/4 heuristic.

    This is a conservative estimate (overestimates tokens).

    Args:
        message: A conversation message with role and content.

    Returns:
        Estimated token count.
    """
    chars = 0
    content = message.get("content", "")

    if isinstance(content, str):
        chars = len(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    chars += len(block.get("text", ""))
                elif block.get("type") == "image":
                    chars += 4800  # Estimate images as 1200 tokens

    return max(1, chars // 4)


class System:
    """Simple workspace system configuration."""

    def __init__(self, workspace_dir: Path) -> None:
        """Initialize the System instance.

        Args:
            workspace_dir: Path to the workspace directory.
        """
        self._workspace_dir = workspace_dir

    async def build_system_prompt(self) -> str:
        """Build system prompt by scanning skills directory asynchronously.

        This function scans the skills/ directory for all SKILL.md files,
        parses their YAML frontmatter to extract descriptions, and combines
        them into a system prompt.

        Returns:
            System prompt string containing skill descriptions and guidelines.
        """
        skills_dir = self._workspace_dir / "skills"
        skill_descriptions: list[str] = []

        if skills_dir.exists():
            for skill_path in skills_dir.iterdir():
                if skill_path.is_dir():
                    skill_md = skill_path / "SKILL.md"
                    if skill_md.exists():
                        description = await _parse_skill_description(skill_md)
                        if description:
                            skill_descriptions.append(f"- {skill_path.name}: {description}")

        system_prompt = f"""You are a helpful assistant with access to tools and skills.

## Workspace

Your workspace directory is: {self._workspace_dir.resolve()}

## Available Skills

"""
        if skill_descriptions:
            system_prompt += "\n".join(skill_descriptions)
        else:
            system_prompt += "No skills configured."

        system_prompt += """

## Guidelines

- Use tools when appropriate to accomplish tasks
- When you need a skill's detailed instructions, read the SKILL.md file
- Be helpful, accurate, and concise
"""

        return system_prompt

    async def compact_history(
        self,
        history: list[dict[str, Any]],
        complete_fn: CompleteFn,
        max_tokens: int = 4000,
        keep_recent_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        """Compact conversation history by keeping recent messages.

        This simple implementation ignores the complete_fn and keep_recent_tokens
        parameters and uses simple truncation. It accepts them for interface
        compatibility with other workspaces.

        Args:
            history: List of conversation messages with role and content.
            complete_fn: Async function for single-turn LLM conversation.
                Ignored in this simple implementation.
            max_tokens: Maximum tokens to keep in history.
            keep_recent_tokens: Ignored in this simple implementation.

        Returns:
            Compacted history list with recent messages only.
        """
        _ = complete_fn  # Ignored: simple workspace uses truncation
        _ = keep_recent_tokens  # Ignored: simple workspace uses truncation

        # Calculate total tokens in history
        total_tokens = sum(_estimate_tokens(msg) for msg in history)

        if total_tokens <= max_tokens:
            return history

        # Walk backwards to find cut point
        accumulated = 0
        cut_index = len(history)

        for i in range(len(history) - 1, -1, -1):
            accumulated += _estimate_tokens(history[i])
            if accumulated >= max_tokens:
                cut_index = i
                break

        result = history[cut_index:]

        # Repair tool_use/tool_result pairing to prevent API errors
        repair_report = _repair_tool_use_result_pairing(result)
        return repair_report.messages
