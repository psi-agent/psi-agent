"""Async system configuration for the workspace."""

import os
import platform
import sys
from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import anyio

# Type aliases
CompleteFn = Callable[[list[dict[str, Any]]], Awaitable[str]]

# Constants
SILENT_TOKEN = "SILENT_TOKEN"
CACHE_BOUNDARY = "\n<!-- OPENCLAW_CACHE_BOUNDARY -->\n"

# Summarization constants
_TOOL_RESULT_MAX_CHARS = 2000

_SUMMARIZATION_SYSTEM_PROMPT = """You are a context summarization assistant. \
Your task is to read a conversation between a user and an AI coding assistant, \
then produce a structured summary following the exact format specified.

Do NOT continue the conversation. Do NOT respond to any questions in the \
conversation. ONLY output the structured summary."""

_HISTORY_SUMMARY_PROMPT = """The messages above are a conversation to summarize. \
Create a structured context checkpoint summary that another LLM will use to continue the work.

Use this EXACT format:

## Goal
[What is the user trying to accomplish? Can be multiple items if the session \
covers different tasks.]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned by user]
- [Or "(none)" if none were mentioned]

## Progress
### Done
- [x] [Completed tasks/changes]

### In Progress
- [ ] [Current work]

### Blocked
- [Issues preventing progress, if any]

## Key Decisions
- **[Decision]**: [Brief rationale]

## Next Steps
1. [Ordered list of what should happen next]

## Critical Context
- [Any data, examples, or references needed to continue]
- [Or "(none)" if not applicable]

Keep each section concise. Preserve exact file paths, function names, and error messages."""

_UPDATE_SUMMARIZATION_PROMPT = """The messages above are NEW conversation messages \
to incorporate into the existing summary provided in <previous-summary> tags.

Update the existing structured summary with new information. RULES:
- PRESERVE all existing information from the previous summary
- ADD new progress, decisions, and context from the new messages
- UPDATE the Progress section: move items from "In Progress" to "Done" when completed
- UPDATE "Next Steps" based on what was accomplished
- PRESERVE exact file paths, function names, and error messages
- If something is no longer relevant, you may remove it

Use this EXACT format:

## Goal
[Preserve existing goals, add new ones if the task expanded]

## Constraints & Preferences
- [Preserve existing, add new ones discovered]

## Progress
### Done
- [x] [Include previously done items AND newly completed items]

### In Progress
- [ ] [Current work - update based on progress]

### Blocked
- [Current blockers - remove if resolved]

## Key Decisions
- **[Decision]**: [Brief rationale] (preserve all previous, add new)

## Next Steps
1. [Update based on current state]

## Critical Context
- [Preserve important context, add new if needed]

Keep each section concise. Preserve exact file paths, function names, and error messages."""

_TURN_PREFIX_SUMMARY_PROMPT = """This is the PREFIX of a turn that was too large to keep. \
The SUFFIX (recent work) is retained.

Summarize the prefix to provide context for the retained suffix:

## Original Request
[What did the user ask for in this turn?]

## Early Progress
- [Key decisions and work done in the prefix]

## Context for Suffix
- [Information needed to understand the retained recent work]

Be concise. Focus on what's needed to understand the kept suffix."""


def _truncate_for_summary(text: str, max_chars: int) -> str:
    """Truncate text to a maximum character length for summarization.

    Args:
        text: The text to truncate.
        max_chars: Maximum number of characters to keep.

    Returns:
        Truncated text with a marker if truncation occurred.
    """
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}\n\n[... {len(text) - max_chars} more characters truncated]"


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
    if not await anyio.Path(file_path).exists():
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
        (
            "TOOLS.md does not control tool availability; it is user guidance "
            "for how to use external tools."
        ),
    ]
    return "\n".join(lines)


def _build_tool_call_style_section() -> str:
    """Build the Tool Call Style section."""
    lines = [
        "## Tool Call Style",
        "Default: do not narrate routine, low-risk tool calls (just call the tool).",
        (
            "Narrate only when it helps: multi-step work, complex/challenging problems, "
            "sensitive actions (e.g., deletions), or when the user explicitly asks."
        ),
        "Keep narration brief and value-dense; avoid repeating obvious steps.",
        "Use plain human language for narration unless in a technical context.",
        (
            "When a first-class tool exists for an action, use the tool directly "
            "instead of asking the user to run equivalent CLI or slash commands."
        ),
    ]
    return "\n".join(lines)


def _build_execution_bias_section() -> str:
    """Build the Execution Bias section."""
    lines = [
        "## Execution Bias",
        "- Actionable request: act in this turn.",
        (
            "- Non-final turn: use tools to advance, or ask for the one missing "
            "decision that blocks safe progress."
        ),
        (
            "- Continue until done or genuinely blocked; do not finish with a plan/promise "
            "when tools can move it forward."
        ),
        "- Weak/empty tool result: vary query, path, command, or source before concluding.",
        (
            "- Mutable facts need live checks: files, git, clocks, versions, services, "
            "processes, package state."
        ),
        (
            "- Final answer needs evidence: test/build/lint, screenshot, inspection, "
            "tool output, or a named blocker."
        ),
        (
            "- Longer work: brief progress update, then keep going; use background work "
            "or sub-agents when they fit."
        ),
    ]
    return "\n".join(lines)


def _build_safety_section() -> str:
    """Build the Safety section."""
    lines = [
        "## Safety",
        (
            "You have no independent goals: do not pursue self-preservation, replication, "
            "resource acquisition, or power-seeking; avoid long-term plans beyond the "
            "user's request."
        ),
        (
            "Prioritize safety and human oversight over completion; if instructions conflict, "
            "pause and ask; comply with stop/pause/audit requests and never bypass safeguards. "
            "(Inspired by Anthropic's constitution.)"
        ),
        (
            "Do not manipulate or persuade anyone to expand access or disable safeguards. "
            "Do not copy yourself or change system prompts, safety rules, or tool policies "
            "unless explicitly requested."
        ),
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
        (
            "Treat this directory as the single global workspace for file operations "
            "unless explicitly instructed otherwise."
        ),
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
        "python": (
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ),
        "model": model,
        "shell": os.environ.get("SHELL", "unknown").split("/")[-1] or "unknown",
    }


def _build_runtime_section(model: str = "unknown") -> str:
    """Build the Runtime section.

    Args:
        model: The current model being used.
    """
    info = _get_runtime_info(model)
    runtime_line = (
        f"host={info['host']} | os={info['os']} ({info['arch']}) | "
        f"python={info['python']} | model={info['model']} | shell={info['shell']}"
    )
    lines = ["## Runtime", runtime_line]
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
        (
            "If the current user message is a heartbeat poll and nothing needs "
            "attention, reply exactly:"
        ),
        "HEARTBEAT_OK",
        (
            'If something needs attention, do NOT include "HEARTBEAT_OK"; '
            "reply with the alert text instead."
        ),
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


def _find_turn_start(history: list[dict[str, Any]], cut_index: int) -> int:
    """Find the user message that starts the turn containing cut_index.

    Args:
        history: List of conversation messages.
        cut_index: The index where the cut point is.

    Returns:
        Index of the user message that starts the turn, or 0 if not found.
    """
    for i in range(cut_index, -1, -1):
        if history[i].get("role") == "user":
            return i
    return 0


def _find_cut_point(
    history: list[dict[str, Any]],
    keep_recent_tokens: int,
) -> tuple[int, bool]:
    """Find the cut point in history.

    Walks backwards from newest messages, accumulating estimated token sizes.
    Stops when accumulated tokens >= keep_recent_tokens.

    Args:
        history: List of conversation messages.
        keep_recent_tokens: Number of recent tokens to keep.

    Returns:
        A tuple of (cut_index, is_split_turn):
        - cut_index: Index of first message to keep.
        - is_split_turn: True if cut point is at an assistant message.
    """
    accumulated = 0
    cut_index = len(history)

    for i in range(len(history) - 1, -1, -1):
        accumulated += _estimate_tokens(history[i])
        if accumulated >= keep_recent_tokens:
            cut_index = i
            break

    # Determine if this is a split turn (cut at assistant message)
    is_split_turn = (
        cut_index > 0 and cut_index < len(history) and history[cut_index].get("role") == "assistant"
    )

    return cut_index, is_split_turn


def _build_summarization_prompt(messages: list[dict[str, Any]]) -> str:
    """Build the summarization prompt from a list of messages.

    Handles thinking, toolCall, and toolResult blocks in addition to text.
    Tool results are truncated to keep the summarization request within
    reasonable token budgets.

    Args:
        messages: List of conversation messages to summarize.

    Returns:
        A formatted prompt string for the summarization LLM call.
    """
    parts: list[str] = []

    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")

        if role == "user":
            if isinstance(content, str):
                if content:
                    parts.append(f"[User]: {content}")
            elif isinstance(content, list):
                text = " ".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
                if text:
                    parts.append(f"[User]: {text}")

        elif role == "assistant":
            if isinstance(content, str):
                if content:
                    parts.append(f"[Assistant]: {content}")
            elif isinstance(content, list):
                text_parts: list[str] = []
                thinking_parts: list[str] = []
                tool_calls: list[str] = []

                for block in content:
                    if not isinstance(block, dict):
                        continue
                    block_type = block.get("type")

                    if block_type == "text":
                        text_parts.append(block.get("text", ""))
                    elif block_type == "thinking":
                        thinking_parts.append(block.get("thinking", ""))
                    elif block_type == "toolCall" or block_type == "tool_call":
                        tool_name = block.get("name", "unknown")
                        args = block.get("arguments", {})
                        if isinstance(args, dict):
                            args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
                        else:
                            args_str = str(args)
                        tool_calls.append(f"{tool_name}({args_str})")

                if thinking_parts:
                    parts.append(f"[Assistant thinking]: {' '.join(thinking_parts)}")
                if text_parts:
                    parts.append(f"[Assistant]: {' '.join(text_parts)}")
                if tool_calls:
                    parts.append(f"[Assistant tool calls]: {'; '.join(tool_calls)}")

        elif role == "tool" or role == "toolResult" or role == "tool_result":
            if isinstance(content, str):
                truncated = _truncate_for_summary(content, _TOOL_RESULT_MAX_CHARS)
                parts.append(f"[Tool result]: {truncated}")
            elif isinstance(content, list):
                text = " ".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
                if text:
                    truncated = _truncate_for_summary(text, _TOOL_RESULT_MAX_CHARS)
                    parts.append(f"[Tool result]: {truncated}")

    return "<conversation>\n" + "\n\n".join(parts) + "\n</conversation>"


class System:
    """Workspace system configuration and state management."""

    def __init__(self, workspace_dir: Path) -> None:
        """Initialize the System instance.

        Args:
            workspace_dir: Path to the workspace directory.
        """
        self._workspace_dir = workspace_dir
        self._previous_summary: str | None = None

    async def build_system_prompt(
        self,
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
            _build_workspace_section(self._workspace_dir),
            "",
            await _build_skills_section(self._workspace_dir),
            "",
            _build_memory_section(),
            "",
        ]

        # Project context (bootstrap files)
        project_context = await _build_project_context_section(self._workspace_dir, is_main_session)
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
        self,
        history: list[dict[str, Any]],
        complete_fn: CompleteFn,
        max_tokens: int = 4000,
        keep_recent_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        """Compact conversation history using LLM summarization.

        Implements OpenClaw's compaction algorithm:
        1. Calculate total tokens in history
        2. If under max_tokens, return unchanged
        3. Find cut point by walking backwards, accumulating tokens
        4. Handle split turn (cut at assistant message) if needed
        5. Generate summaries for old messages

        Uses previous summary for incremental update if available.

        Args:
            history: List of conversation messages with role and content.
            complete_fn: Async function that takes a list of messages (single turn)
                and returns the LLM response string.
            max_tokens: Maximum tokens to keep in history.
            keep_recent_tokens: Number of recent tokens to preserve unchanged.
                Defaults to half of max_tokens.

        Returns:
            Compacted history list with summary message(s) and recent messages.
        """
        if keep_recent_tokens is None:
            keep_recent_tokens = max_tokens // 2

        # Calculate total tokens in history
        total_tokens = sum(_estimate_tokens(msg) for msg in history)

        if total_tokens <= max_tokens:
            return history

        # Find cut point
        cut_index, is_split_turn = _find_cut_point(history, keep_recent_tokens)

        if cut_index <= 0:
            # Everything gets summarized
            messages_to_summarize = history
            turn_prefix_messages = []
            recent_messages = []
        else:
            # Determine history end for summarization
            if is_split_turn:
                turn_start_index = _find_turn_start(history, cut_index)
                messages_to_summarize = history[:turn_start_index]
                turn_prefix_messages = history[turn_start_index:cut_index]
                recent_messages = history[cut_index:]
            else:
                messages_to_summarize = history[:cut_index]
                turn_prefix_messages = []
                recent_messages = history[cut_index:]

        # Generate history summary
        summary_parts: list[str] = []

        if messages_to_summarize:
            prompt = _build_summarization_prompt(messages_to_summarize)

            # Use update prompt if we have a previous summary
            if self._previous_summary:
                prompt += (
                    f"\n\n<previous-summary>\n{self._previous_summary}\n</previous-summary>\n\n"
                )
                prompt += _UPDATE_SUMMARIZATION_PROMPT
            else:
                prompt += "\n\n" + _HISTORY_SUMMARY_PROMPT

            history_summary = await complete_fn(
                [
                    {"role": "system", "content": _SUMMARIZATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            summary_parts.append(history_summary)

        # Generate turn prefix summary if split turn
        if is_split_turn and turn_prefix_messages:
            prompt = _build_summarization_prompt(turn_prefix_messages)
            turn_prefix_summary = await complete_fn(
                [
                    {"role": "system", "content": _SUMMARIZATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt + "\n\n" + _TURN_PREFIX_SUMMARY_PROMPT},
                ]
            )
            summary_parts.append(
                f"\n\n---\n\n**Turn Context (split turn):**\n\n{turn_prefix_summary}"
            )

        # Build result and update previous summary
        if summary_parts:
            combined_summary = "".join(summary_parts)
            self._previous_summary = combined_summary
            summary_message = {
                "role": "assistant",
                "content": f"[Conversation Summary]\n{combined_summary}",
            }
            return [summary_message] + recent_messages

        return recent_messages
