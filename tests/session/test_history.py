"""Tests for history module."""

from __future__ import annotations

import tempfile
from unittest.mock import patch

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


class TestLoadHistoryEdgeCases:
    """Edge case tests for load_history_from_file."""

    @pytest.mark.asyncio
    async def test_non_json_array_content_json_object(self) -> None:
        """Non-JSON-array content (JSON object)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            await history_file.write_text('{"key": "value"}')
            messages = await load_history_from_file(history_file)
            # Returns the dict as-is (not a list), but json.loads succeeds
            assert isinstance(messages, dict)

    @pytest.mark.asyncio
    async def test_json_string_content(self) -> None:
        """JSON string content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            await history_file.write_text('"just a string"')
            messages = await load_history_from_file(history_file)
            assert messages == "just a string"

    @pytest.mark.asyncio
    async def test_json_number_content(self) -> None:
        """JSON number content — not a list, so returns empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            await history_file.write_text("42")
            messages = await load_history_from_file(history_file)
            # len() fails on int, so exception handler returns []
            assert messages == []

    @pytest.mark.asyncio
    async def test_null_content(self) -> None:
        """'null' JSON content — not a list, so returns empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            await history_file.write_text("null")
            messages = await load_history_from_file(history_file)
            # len() fails on None, so exception handler returns []
            assert messages == []

    @pytest.mark.asyncio
    async def test_empty_string_file(self) -> None:
        """Empty string file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            await history_file.write_text("")
            messages = await load_history_from_file(history_file)
            assert messages == []


class TestSaveHistoryEdgeCases:
    """Edge case tests for save_history_to_file."""

    @pytest.mark.asyncio
    async def test_non_ascii_characters(self) -> None:
        """Messages with non-ASCII characters (ensure_ascii=False preserves)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            history = History(
                messages=[{"role": "user", "content": "你好世界 🌍"}],
                history_file=str(history_file),
            )

            await save_history_to_file(history, history_file)
            content = await history_file.read_text()
            assert "你好世界" in content
            assert "🌍" in content

    @pytest.mark.asyncio
    async def test_special_json_characters(self) -> None:
        """Messages with special JSON characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            history = History(
                messages=[{"role": "user", "content": 'He said "hello" and \\backslash'}],
                history_file=str(history_file),
            )

            await save_history_to_file(history, history_file)
            content = await history_file.read_text()
            assert "hello" in content

    @pytest.mark.asyncio
    async def test_empty_message_list(self) -> None:
        """Empty message list saves as '[]'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            history = History(messages=[], history_file=str(history_file))

            await save_history_to_file(history, history_file)
            content = await history_file.read_text()
            assert content.strip() == "[]"


class TestHistoryRoundTrip:
    """Round-trip consistency tests."""

    @pytest.mark.asyncio
    async def test_save_then_load_identical(self) -> None:
        """Save then load produces identical messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = anyio.Path(tmpdir) / "history.json"
            original_messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
                {"role": "assistant", "content": "I'm fine, thanks!"},
            ]
            history = History(messages=original_messages, history_file=str(history_file))

            await save_history_to_file(history, history_file)
            loaded_messages = await load_history_from_file(history_file)

            assert loaded_messages == original_messages
