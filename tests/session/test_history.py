"""Tests for history module."""

import tempfile
from pathlib import Path

from psi_agent.session.history import (
    initialize_history,
    load_history_from_file,
    persist_history,
    save_history_to_file,
)
from psi_agent.session.types import History


def test_initialize_history_no_file():
    """Test history initialization without file."""
    history = initialize_history(None)
    assert history.messages == []
    assert history.history_file is None


def test_initialize_history_with_file():
    """Test history initialization with file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "history.json"
        history_file.write_text('[{"role": "user", "content": "test"}]')

        history = initialize_history(str(history_file))
        assert len(history.messages) == 1
        assert history.messages[0]["role"] == "user"
        assert history.history_file == str(history_file)


def test_initialize_history_empty_file():
    """Test history initialization with empty file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "history.json"
        history_file.write_text("")

        history = initialize_history(str(history_file))
        assert history.messages == []


def test_load_history_from_file_corrupted():
    """Test loading corrupted JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "history.json"
        history_file.write_text("not valid json")

        messages = load_history_from_file(history_file)
        assert messages == []


def test_save_history_to_file():
    """Test saving history to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "history.json"
        history = History(
            messages=[{"role": "user", "content": "hello"}],
            history_file=str(history_file),
        )

        save_history_to_file(history, history_file)

        content = history_file.read_text()
        assert "hello" in content
        assert "user" in content


def test_persist_history():
    """Test persist_history function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "history.json"
        history = History(
            messages=[{"role": "assistant", "content": "response"}],
            history_file=str(history_file),
        )

        persist_history(history)

        assert history_file.exists()
        content = history_file.read_text()
        assert "response" in content


def test_persist_history_no_file():
    """Test persist_history with no file configured."""
    history = History(messages=[{"role": "user", "content": "test"}], history_file=None)

    # Should not raise error
    persist_history(history)


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
