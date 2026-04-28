"""Async system configuration for the workspace."""

import re
from pathlib import Path


async def build_system_prompt() -> str:
    """Build system prompt by scanning skills directory asynchronously.

    This function scans the skills/ directory for all SKILL.md files,
    parses their YAML frontmatter to extract descriptions, and combines
    them into a system prompt.

    Returns:
        System prompt string containing skill descriptions and guidelines.
    """
    workspace = Path(__file__).parent.parent
    skills_dir = workspace / "skills"
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

Your workspace directory is: {workspace.resolve()}

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


async def _parse_skill_description(skill_md_path: Path) -> str | None:
    """Parse SKILL.md to extract description from YAML frontmatter.

    Args:
        skill_md_path: Path to the SKILL.md file.

    Returns:
        Description string if found, None otherwise.
    """
    # Note: For simplicity, we use synchronous file read here.
    # In production, use aiofiles for async file I/O.
    # Example with aiofiles:
    #   async with aiofiles.open(skill_md_path) as f:
    #       content = await f.read()
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


async def compact_history(
    history: list[dict[str, str]], max_tokens: int = 4000
) -> list[dict[str, str]]:
    """Compact conversation history using LLM summarization.

    This function compresses long conversation histories by summarizing
    older messages while preserving recent context.

    Args:
        history: List of conversation messages with role and content.
        max_tokens: Maximum tokens to keep in history.

    Returns:
        Compacted history list.

    Note:
        This is a framework implementation. The actual LLM summarization
        logic should be implemented based on the specific agent's needs.
    """
    # Framework implementation - placeholder for LLM summarization
    # In production, this would:
    # 1. Count tokens in history
    # 2. If over limit, summarize older messages via LLM API (async)
    # 3. Return compacted history with summary + recent messages

    # Simple implementation: keep last N messages
    # (This should be replaced with proper LLM summarization)
    max_messages = 20  # Approximate message limit
    if len(history) > max_messages:
        return history[-max_messages:]

    return history
