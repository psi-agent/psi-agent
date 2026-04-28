"""Async system configuration for the workspace."""

from pathlib import Path
from typing import Any

import anyio


def _strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter from file content.

    Args:
        content: The file content to strip frontmatter from.

    Returns:
        Content with frontmatter removed, or original content if no frontmatter.
    """
    if not content.startswith("---"):
        return content
    end_index = content.find("\n---", 3)
    if end_index == -1:
        return content
    start = end_index + len("\n---")
    trimmed = content[start:]
    trimmed = trimmed.lstrip("\n")
    return trimmed


async def _read_bootstrap_file(file_path: Path) -> str | None:
    """Read a bootstrap file asynchronously.

    Args:
        file_path: Path to the file to read.

    Returns:
        File content with frontmatter stripped, or None if file doesn't exist.
    """
    if not file_path.exists():
        return None
    try:
        async with await anyio.open_file(file_path, encoding="utf-8") as f:
            content = await f.read()
        return _strip_frontmatter(content)
    except OSError:
        return None


async def build_system_prompt(
    is_main_session: bool = True,
) -> str:
    """Build system prompt by loading bootstrap files.

    Loads bootstrap files in order: AGENTS.md → SOUL.md → TOOLS.md →
    IDENTITY.md → USER.md → HEARTBEAT.md → BOOTSTRAP.md → MEMORY.md

    MEMORY.md is only loaded in main sessions for privacy protection.

    Args:
        is_main_session: Whether this is a main session (direct chat with user).
            If False, MEMORY.md will not be loaded.

    Returns:
        System prompt string containing all bootstrap file contents.
    """
    workspace = Path(__file__).parent.parent

    bootstrap_files = [
        "AGENTS.md",
        "SOUL.md",
        "TOOLS.md",
        "IDENTITY.md",
        "USER.md",
        "HEARTBEAT.md",
        "BOOTSTRAP.md",
    ]

    sections: list[str] = []

    for filename in bootstrap_files:
        file_path = workspace / filename
        content = await _read_bootstrap_file(file_path)
        if content is not None:
            sections.append(f"## {filename}\n\n{content}")

    # Only load MEMORY.md in main session for privacy
    if is_main_session:
        memory_path = workspace / "MEMORY.md"
        memory_content = await _read_bootstrap_file(memory_path)
        if memory_content is not None:
            sections.append(f"## MEMORY.md\n\n{memory_content}")

    return "\n\n---\n\n".join(sections)


async def compact_history(
    history: list[dict[str, Any]], max_tokens: int = 4000
) -> list[dict[str, Any]]:
    """Compact conversation history by keeping recent messages.

    This is a simple implementation that keeps the last N messages.
    In production, this could use LLM summarization for better context preservation.

    Args:
        history: List of conversation messages with role and content.
        max_tokens: Maximum tokens to keep in history (approximate).

    Returns:
        Compacted history list with recent messages.
    """
    # Simple implementation: keep last N messages
    # Approximate 4 tokens per message on average
    max_messages = max(20, max_tokens // 4)
    if len(history) > max_messages:
        return history[-max_messages:]
    return history
