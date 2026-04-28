"""Conversation history management and persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anyio
from loguru import logger

from psi_agent.session.types import History


async def load_history_from_file(history_file: Path | anyio.Path) -> list[dict[str, Any]]:
    """Load history from JSON file.

    Args:
        history_file: Path to the JSON file.

    Returns:
        List of messages, empty list if file doesn't exist or is corrupted.
    """
    if not await anyio.Path(history_file).exists():
        logger.debug(f"History file does not exist: {history_file}")
        return []

    try:
        content = await anyio.Path(history_file).read_text()
        messages = json.loads(content)
        logger.info(f"Loaded {len(messages)} messages from history file")
        return messages
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse history file: {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load history file: {e}")
        return []


async def save_history_to_file(history: History, history_file: Path | anyio.Path) -> None:
    """Save history to JSON file.

    Args:
        history: History object to save.
        history_file: Path to the JSON file.
    """
    try:
        content = json.dumps(history.messages, ensure_ascii=False, indent=2)
        await anyio.Path(history_file).write_text(content)
        logger.debug(f"Saved {len(history.messages)} messages to history file")
    except Exception as e:
        logger.error(f"Failed to save history file: {e}")


async def initialize_history(history_file: str | None) -> History:
    """Initialize history, optionally loading from file.

    Args:
        history_file: Optional path to history JSON file.

    Returns:
        Initialized History object.
    """
    if history_file is None:
        logger.debug("No history file specified, using memory-only history")
        return History(messages=[], history_file=None)

    history_path = anyio.Path(history_file)
    messages = await load_history_from_file(history_path)
    return History(messages=messages, history_file=history_file)


async def persist_history(history: History) -> None:
    """Persist history to file if configured.

    Args:
        history: History object to persist.
    """
    if history.history_file is None:
        return

    history_path = anyio.Path(history.history_file)
    await save_history_to_file(history, history_path)
