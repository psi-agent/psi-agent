"""Async system configuration for the workspace."""

# ruff: noqa: E501

import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import anyio

# Constants
SILENT_TOKEN = "SILENT_TOKEN"
CACHE_BOUNDARY = "\n<!-- OPENCLAW_CACHE_BOUNDARY -->\n"


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


def _build_identity_section() -> str:
    """Build the identity statement section."""
    return "You are a personal assistant running inside OpenClaw."


def _build_tooling_section() -> str:
    """Build the Tooling section with available tools."""
    tools = [
        "- read: Read file contents",
        "- write: Create or overwrite files",
        "- edit: Make precise edits to files",
        "- bash: Run shell commands with timeout support",
    ]
    lines = [
        "## Tooling",
        "Tool availability (filtered by policy):",
        "Tool names are case-sensitive. Call tools exactly as listed.",
        *tools,
        "TOOLS.md does not control tool availability; it is user guidance for how to use external tools.",
    ]
    return "\n".join(lines)


def _build_tool_call_style_section() -> str:
    """Build the Tool Call Style section."""
    lines = [
        "## Tool Call Style",
        "Default: do not narrate routine, low-risk tool calls (just call the tool).",
        "Narrate only when it helps: multi-step work, complex/challenging problems, sensitive actions (e.g., deletions), or when the user explicitly asks.",
        "Keep narration brief and value-dense; avoid repeating obvious steps.",
        "Use plain human language for narration unless in a technical context.",
        "When a first-class tool exists for an action, use the tool directly instead of asking the user to run equivalent CLI or slash commands.",
    ]
    return "\n".join(lines)


def _build_execution_bias_section() -> str:
    """Build the Execution Bias section."""
    lines = [
        "## Execution Bias",
        "- Actionable request: act in this turn.",
        "- Non-final turn: use tools to advance, or ask for the one missing decision that blocks safe progress.",
        "- Continue until done or genuinely blocked; do not finish with a plan/promise when tools can move it forward.",
        "- Weak/empty tool result: vary query, path, command, or source before concluding.",
        "- Mutable facts need live checks: files, git, clocks, versions, services, processes, package state.",
        "- Final answer needs evidence: test/build/lint, screenshot, inspection, tool output, or a named blocker.",
        "- Longer work: brief progress update, then keep going; use background work or sub-agents when they fit.",
    ]
    return "\n".join(lines)


def _build_safety_section() -> str:
    """Build the Safety section."""
    lines = [
        "## Safety",
        "You have no independent goals: do not pursue self-preservation, replication, resource acquisition, or power-seeking; avoid long-term plans beyond the user's request.",
        "Prioritize safety and human oversight over completion; if instructions conflict, pause and ask; comply with stop/pause/audit requests and never bypass safeguards. (Inspired by Anthropic's constitution.)",
        "Do not manipulate or persuade anyone to expand access or disable safeguards. Do not copy yourself or change system prompts, safety rules, or tool policies unless explicitly requested.",
    ]
    return "\n".join(lines)


def _build_workspace_section(workspace_dir: Path) -> str:
    """Build the Workspace section.

    Args:
        workspace_dir: Path to the workspace directory.
    """
    lines = [
        "## Workspace",
        f"Your working directory is: {workspace_dir.resolve()}",
        "Treat this directory as the single global workspace for file operations unless explicitly instructed otherwise.",
    ]
    return "\n".join(lines)


def _get_runtime_info(model: str = "unknown") -> dict[str, str]:
    """Get runtime information using Python standard library.

    Args:
        model: The current model being used.

    Returns:
        Dictionary with runtime information.
    """
    return {
        "host": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.machine(),
        "python": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "model": model,
        "shell": os.environ.get("SHELL", "unknown").split("/")[-1] or "unknown",
    }


def _build_runtime_section(model: str = "unknown") -> str:
    """Build the Runtime section.

    Args:
        model: The current model being used.
    """
    info = _get_runtime_info(model)
    lines = [
        "## Runtime",
        f"host={info['host']} | os={info['os']} ({info['arch']}) | python={info['python']} | model={info['model']} | shell={info['shell']}",
    ]
    return "\n".join(lines)


def _build_datetime_section(timezone: str = "UTC") -> str:
    """Build the Current Date & Time section.

    Args:
        timezone: The user's timezone.
    """
    now = datetime.now()
    lines = [
        "## Current Date & Time",
        f"Date: {now.strftime('%Y-%m-%d')}",
        f"Time: {now.strftime('%H:%M:%S')}",
        f"Time zone: {timezone}",
    ]
    return "\n".join(lines)


async def _build_skills_section(workspace: Path) -> str:
    """Build the Skills section by scanning skills directory.

    Args:
        workspace: Path to the workspace directory.
    """
    skills_dir = workspace / "skills"
    skill_descriptions: list[str] = []

    if skills_dir.exists():
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    content = await _read_bootstrap_file(skill_md)
                    if content:
                        # Extract first line as description
                        first_line = content.split("\n")[0].strip()
                        if first_line:
                            skill_descriptions.append(f"- {skill_path.name}: {first_line}")

    lines = [
        "## Skills (mandatory)",
        "Before replying: scan available skills and their descriptions.",
        "- If exactly one skill clearly applies: read its SKILL.md, then follow it.",
        "- If multiple could apply: choose the most specific one, then read/follow it.",
        "- If none clearly apply: do not read any SKILL.md.",
        "Constraints: never read more than one skill up front; only read after selecting.",
    ]

    if skill_descriptions:
        lines.append("")
        lines.append("Available skills:")
        lines.extend(skill_descriptions)

    return "\n".join(lines)


def _build_memory_section() -> str:
    """Build the Memory section."""
    lines = [
        "## Memory",
        "MEMORY.md is your long-term memory. You can read, edit, and update it freely.",
        "- Write significant events, decisions, and things worth remembering.",
        "- This is your curated memory, not raw logs.",
        "- Over time, review and distill important information into MEMORY.md.",
    ]
    return "\n".join(lines)


def _build_heartbeats_section() -> str:
    """Build the Heartbeats section."""
    lines = [
        "## Heartbeats",
        "If the current user message is a heartbeat poll and nothing needs attention, reply exactly:",
        "HEARTBEAT_OK",
        'If something needs attention, do NOT include "HEARTBEAT_OK"; reply with the alert text instead.',
    ]
    return "\n".join(lines)


def _build_silent_replies_section() -> str:
    """Build the Silent Replies section."""
    lines = [
        "## Silent Replies",
        f"When you have nothing to say, respond with ONLY: {SILENT_TOKEN}",
        "",
        "Rules:",
        "- It must be your ENTIRE message — nothing else",
        f'- Never append it to an actual response (never include "{SILENT_TOKEN}" in real replies)',
        "- Never wrap it in markdown or code blocks",
    ]
    return "\n".join(lines)


async def _build_project_context_section(workspace: Path, is_main_session: bool) -> str:
    """Build the Project Context section with bootstrap files.

    Args:
        workspace: Path to the workspace directory.
        is_main_session: Whether this is a main session.
    """
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

    if not sections:
        return ""

    header = "# Project Context\n\nThe following project context files have been loaded:\n"
    return header + "\n\n".join(sections)


async def build_system_prompt(
    is_main_session: bool = True,
    model: str = "unknown",
    timezone: str = "UTC",
) -> str:
    """Build system prompt by combining all sections.

    Section order:
    1. Identity
    2. Tooling
    3. Tool Call Style
    4. Execution Bias
    5. Safety
    6. Workspace
    7. Skills
    8. Memory
    9. Project Context (bootstrap files)
    10. Cache Boundary
    11. Heartbeats
    12. Silent Replies
    13. Current Date & Time
    14. Runtime

    Args:
        is_main_session: Whether this is a main session (direct chat with user).
            If False, MEMORY.md will not be loaded.
        model: The current model being used.
        timezone: The user's timezone.

    Returns:
        System prompt string containing all sections.
    """
    workspace = Path(__file__).parent.parent

    # Stable sections (before cache boundary)
    stable_sections = [
        _build_identity_section(),
        "",
        _build_tooling_section(),
        "",
        _build_tool_call_style_section(),
        "",
        _build_execution_bias_section(),
        "",
        _build_safety_section(),
        "",
        _build_workspace_section(workspace),
        "",
        await _build_skills_section(workspace),
        "",
        _build_memory_section(),
        "",
    ]

    # Project context (bootstrap files)
    project_context = await _build_project_context_section(workspace, is_main_session)
    if project_context:
        stable_sections.append(project_context)
        stable_sections.append("")

    # Dynamic sections (after cache boundary)
    dynamic_sections = [
        _build_heartbeats_section(),
        "",
        _build_silent_replies_section(),
        "",
        _build_datetime_section(timezone),
        "",
        _build_runtime_section(model),
    ]

    # Combine all sections
    prompt = "\n".join(stable_sections) + CACHE_BOUNDARY + "\n".join(dynamic_sections)
    return prompt


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
