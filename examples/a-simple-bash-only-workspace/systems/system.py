"""Simple workspace system configuration."""

import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

# Type aliases
CompleteFn = Callable[[list[dict[str, Any]]], Awaitable[str]]


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


class System:
    """Simple workspace system configuration."""

    def __init__(self, workspace_dir: Path) -> None:
        """Initialize the System instance.

        Args:
            workspace_dir: Path to the workspace directory.
        """
        self._workspace_dir = workspace_dir

    async def build_system_prompt(self) -> str:
        """Build system prompt by scanning skills directory.

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

        lines = [
            f"You are a helpful assistant. Workspace: {self._workspace_dir.resolve()}",
            "",
            "## Available Skills",
        ]

        if skill_descriptions:
            lines.extend(skill_descriptions)
        else:
            lines.append("No skills configured.")

        lines.extend(
            [
                "",
                "## Guidelines",
                "- Use tools when appropriate",
                "- Read SKILL.md for skill details",
                "- Be helpful and concise",
            ]
        )

        return "\n".join(lines)

    async def compact_history(
        self,
        history: list[dict[str, Any]],
        complete_fn: CompleteFn,
        max_tokens: int = 4000,
        keep_recent_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        """Compact history by keeping the most recent 20 messages.

        Args:
            history: List of conversation messages.
            complete_fn: Ignored (interface compatibility).
            max_tokens: Ignored (interface compatibility).
            keep_recent_tokens: Ignored (interface compatibility).

        Returns:
            Most recent 20 messages.
        """
        _ = complete_fn, max_tokens, keep_recent_tokens  # Ignored
        return history[-20:] if len(history) > 20 else history
