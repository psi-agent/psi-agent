"""Tests for history module."""

from __future__ import annotations

import tempfile

import anyio
import pytest

from psi_agent.session.history import (
    initialize_history,
    load_history_from_file,
    persist_history,
    save_history_to_file,
)
from psi_agent.session.types import History


@pytest.mark.asyncio
async def test_initialize_history_no_file():
    """Test history initialization without file."""
    history = await initialize_history(None)
    assert history.messages == []
    assert history.history_file is None


@pytest.mark.asyncio
async def test_initialize_history_with_file():
    """Test history initialization with file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        await history_file.write_text('[{"role": "user", "content": "test"}]')

        history = await initialize_history(str(history_file))
        assert len(history.messages) == 1
        assert history.messages[0]["role"] == "user"
        assert history.history_file == str(history_file)


@pytest.mark.asyncio
async def test_initialize_history_empty_file():
    """Test history initialization with empty file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        await history_file.write_text("")

        history = await initialize_history(str(history_file))
        assert history.messages == []


@pytest.mark.asyncio
async def test_load_history_from_file_corrupted():
    """Test loading corrupted JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        await history_file.write_text("not valid json")

        messages = await load_history_from_file(history_file)
        assert messages == []


@pytest.mark.asyncio
async def test_save_history_to_file():
    """Test saving history to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        history = History(
            messages=[{"role": "user", "content": "hello"}],
            history_file=str(history_file),
        )

        await save_history_to_file(history, history_file)

        content = await history_file.read_text()
        assert "hello" in content
        assert "user" in content


@pytest.mark.asyncio
async def test_persist_history():
    """Test persist_history function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        history = History(
            messages=[{"role": "assistant", "content": "response"}],
            history_file=str(history_file),
        )

        await persist_history(history)

        assert await history_file.exists()
        content = await history_file.read_text()
        assert "response" in content


@pytest.mark.asyncio
async def test_persist_history_no_file():
    """Test persist_history with no file configured."""
    history = History(messages=[{"role": "user", "content": "test"}], history_file=None)

    # Should not raise error
    await persist_history(history)


def test_history_add_message():
    """Test adding messages to history."""
    history = History()

    history.add_message({"role": "user", "content": "hello"})
    history.add_message({"role": "assistant", "content": "hi"})

    assert len(history.messages) == 2
    assert history.messages[0]["role"] == "user"
    assert history.messages[1]["role"] == "assistant"


def test_history_clear():
    """Test clearing history."""
    history = History(messages=[{"role": "user", "content": "test"}])

    history.clear()

    assert len(history.messages) == 0


def test_history_multiple_adds():
    """Test adding multiple messages preserves order."""
    history = History()

    for i in range(5):
        history.add_message({"role": "user" if i % 2 == 0 else "assistant", "content": f"msg{i}"})

    assert len(history.messages) == 5
    assert history.messages[0]["content"] == "msg0"
    assert history.messages[4]["content"] == "msg4"


@pytest.mark.asyncio
async def test_save_history_creates_parent_dirs():
    """Test saving history - parent dirs must exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Parent directories must exist - save_history_to_file doesn't create them
        history_file = anyio.Path(tmpdir) / "subdir" / "history.json"
        await history_file.parent.mkdir(parents=True, exist_ok=True)

        history = History(
            messages=[{"role": "user", "content": "test"}],
            history_file=str(history_file),
        )

        await save_history_to_file(history, history_file)

        assert await history_file.exists()


@pytest.mark.asyncio
async def test_load_history_nonexistent_file():
    """Test loading from nonexistent file returns empty list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "nonexistent.json"

        messages = await load_history_from_file(history_file)
        assert messages == []


@pytest.mark.asyncio
async def test_load_history_permission_error():
    """Test loading history when permission denied."""
    # Mock the permission error scenario
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        await history_file.write_text('[{"role": "user", "content": "test"}]')

        # Mock read_text to raise permission error
        with patch.object(anyio.Path, "read_text", side_effect=PermissionError("Access denied")):
            messages = await load_history_from_file(history_file)
            assert messages == []


@pytest.mark.asyncio
async def test_save_history_write_error():
    """Test saving history when write fails."""
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = anyio.Path(tmpdir) / "history.json"
        history = History(
            messages=[{"role": "user", "content": "hello"}],
            history_file=str(history_file),
        )

        # Mock write_text to raise error
        with patch.object(anyio.Path, "write_text", side_effect=OSError("Write failed")):
            # Should not raise error, just log it
            await save_history_to_file(history, history_file)
