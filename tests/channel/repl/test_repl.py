"""Tests for REPL interface."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest
from prompt_toolkit.history import FileHistory

from psi_agent.channel.repl.config import ReplConfig
from psi_agent.channel.repl.repl import Repl, _ensure_history_dir


class TestRepl:
    """Tests for Repl."""

    @pytest.fixture
    def config(self) -> ReplConfig:
        """Create test config."""
        return ReplConfig(session_socket="/tmp/test.sock")

    @pytest.fixture
    def repl(self, config: ReplConfig) -> Repl:
        """Create test REPL."""
        return Repl(config)

    def test_repl_creation(self, repl: Repl, config: ReplConfig) -> None:
        """Test REPL creation."""
        assert repl.config == config

    def test_repl_has_client(self, repl: Repl) -> None:
        """Test REPL has client."""
        assert repl.client is not None

    def test_repl_session_initialized_on_run(self, repl: Repl) -> None:
        """Test PromptSession is initialized when run starts."""
        assert repl._session is None

    @pytest.mark.asyncio
    async def test_read_input_with_session(self, repl: Repl) -> None:
        """Test reading input with prompt-toolkit session."""
        # Initialize session
        repl._session = MagicMock()
        repl._session.prompt_async = AsyncMock(return_value="Hello")

        result = await repl._read_input()
        assert result == "Hello"

    @pytest.mark.asyncio
    async def test_read_input_eof(self, repl: Repl) -> None:
        """Test reading input with EOF."""
        repl._session = MagicMock()
        repl._session.prompt_async = AsyncMock(side_effect=EOFError())

        result = await repl._read_input()
        assert result is None

    @pytest.mark.asyncio
    async def test_read_input_no_session(self, repl: Repl) -> None:
        """Test reading input when session is not initialized."""
        repl._session = None
        result = await repl._read_input()
        assert result is None

    @pytest.mark.asyncio
    async def test_eof_exits_repl(self, repl: Repl) -> None:
        """Test EOF (Ctrl+D) exits REPL."""
        inputs = [None]  # EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with patch.object(repl, "_read_input", mock_read), patch("builtins.print") as mock_print:
            await repl.run()

            # Check goodbye message was printed
            assert any("Goodbye" in str(call) for call in mock_print.call_args_list)

    @pytest.mark.asyncio
    async def test_keyboard_interrupt_exits_repl(self, repl: Repl) -> None:
        """Test Ctrl+C exits REPL."""

        async def mock_read() -> str | None:
            raise KeyboardInterrupt()

        with patch.object(repl, "_read_input", mock_read), patch("builtins.print") as mock_print:
            await repl.run()

            # Check goodbye message was printed
            assert any("Goodbye" in str(call) for call in mock_print.call_args_list)

    @pytest.mark.asyncio
    async def test_empty_input_ignored(self, repl: Repl) -> None:
        """Test empty input is ignored."""
        inputs = ["", None]  # Empty string, then EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        mock_send = AsyncMock(return_value="Response")
        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", mock_send),
            patch("builtins.print"),
        ):
            await repl.run()

            # send_message should not have been called for empty input
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_message_sent_to_session(self, repl: Repl) -> None:
        """Test message is sent to session."""
        inputs = ["Hello", None]  # Message, then EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        mock_send_stream = AsyncMock(return_value="Hi there!")
        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message_stream", mock_send_stream),
            patch("builtins.print"),
        ):
            await repl.run()

            # send_message_stream should be called with the user input
            assert mock_send_stream.called
            call_args = mock_send_stream.call_args
            assert call_args[0][0] == "Hello"


class TestReplHistory:
    """Tests for REPL history navigation."""

    @pytest.fixture
    def config(self, tmp_path) -> ReplConfig:
        """Create test config with custom history file."""
        history_file = anyio.Path(tmp_path) / "history.txt"
        return ReplConfig(session_socket="/tmp/test.sock", history_file=str(history_file))

    @pytest.fixture
    def repl(self, config: ReplConfig) -> Repl:
        """Create test REPL."""
        return Repl(config)

    @pytest.mark.asyncio
    async def test_history_stored_in_session(self, repl: Repl) -> None:
        """Test that inputs are stored in prompt-toolkit history."""
        inputs = ["First message", "Second message", None]  # Messages, then EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", AsyncMock(return_value="Response")),
            patch("builtins.print"),
        ):
            await repl.run()

            # Session should have FileHistory
            assert repl._session is not None
            assert isinstance(repl._session.history, FileHistory)

    @pytest.mark.asyncio
    async def test_history_persists_to_file(self, tmp_path) -> None:
        """Test that FileHistory is created with correct path."""
        history_file = anyio.Path(tmp_path) / "history.txt"
        config = ReplConfig(session_socket="/tmp/test.sock", history_file=str(history_file))
        repl = Repl(config)

        inputs = ["First message", None]  # Message, then EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", AsyncMock(return_value="Response")),
            patch("builtins.print"),
        ):
            await repl.run()

            # Session should have FileHistory with correct path
            assert repl._session is not None
            assert isinstance(repl._session.history, FileHistory)
            # FileHistory stores the filename
            assert repl._session.history.filename == str(history_file)

    @pytest.mark.asyncio
    async def test_history_loaded_from_file(self, tmp_path) -> None:
        """Test that FileHistory can load from existing file."""
        history_file = anyio.Path(tmp_path) / "history.txt"
        # Pre-populate history file in FileHistory format
        await history_file.write_text("\n# 2026-04-29 00:00:00\n+Previous entry\n")

        config = ReplConfig(session_socket="/tmp/test.sock", history_file=str(history_file))
        repl = Repl(config)

        inputs = [None]  # EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", AsyncMock(return_value="Response")),
            patch("builtins.print"),
        ):
            await repl.run()

            # Session should have FileHistory that can read existing entries
            assert repl._session is not None
            assert isinstance(repl._session.history, FileHistory)
            # FileHistory loads existing entries
            history_items = list(repl._session.history.load_history_strings())
            assert "Previous entry" in history_items

    @pytest.mark.asyncio
    async def test_multiline_input_preserved(self, repl: Repl) -> None:
        """Test multiline input is preserved with line breaks."""
        multiline_input = "Line 1\nLine 2\nLine 3"
        inputs = [multiline_input, None]  # Message, then EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        mock_send_stream = AsyncMock(return_value="Response")
        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message_stream", mock_send_stream),
            patch("builtins.print"),
        ):
            await repl.run()

            # Check multiline message preserved
            assert mock_send_stream.called
            call_args = mock_send_stream.call_args
            assert call_args[0][0] == multiline_input


class TestReplEditing:
    """Tests for REPL line editing capabilities."""

    @pytest.fixture
    def config(self, tmp_path) -> ReplConfig:
        """Create test config with custom history file."""
        history_file = anyio.Path(tmp_path) / "history.txt"
        return ReplConfig(session_socket="/tmp/test.sock", history_file=str(history_file))

    @pytest.fixture
    def repl(self, config: ReplConfig) -> Repl:
        """Create test REPL."""
        return Repl(config)

    @pytest.mark.asyncio
    async def test_prompt_session_created(self, repl: Repl) -> None:
        """Test that PromptSession is created during run."""
        inputs = [None]  # EOF
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with patch.object(repl, "_read_input", mock_read), patch("builtins.print"):
            await repl.run()

            # Session should be created
            assert repl._session is not None

    @pytest.mark.asyncio
    async def test_prompt_async_called(self, repl: Repl) -> None:
        """Test that prompt_async is called with correct parameters."""
        repl._session = MagicMock()
        repl._session.prompt_async = AsyncMock(return_value="test")
        repl._session.history = FileHistory(":memory:")

        _ = await repl._read_input()

        # Verify prompt_async was called
        repl._session.prompt_async.assert_called_once()
        call_args = repl._session.prompt_async.call_args
        assert call_args[0][0] == "> "  # prompt string
        assert call_args[1]["multiline"] is True  # multiline enabled


class TestEnsureHistoryDir:
    """Tests for _ensure_history_dir helper function."""

    @pytest.mark.asyncio
    async def test_creates_directory_if_missing(self, tmp_path) -> None:
        """Test that directory is created when it doesn't exist."""
        history_path = anyio.Path(tmp_path) / "subdir" / "history.txt"
        assert not await history_path.parent.exists()

        await _ensure_history_dir(history_path)

        assert await history_path.parent.exists()

    @pytest.mark.asyncio
    async def test_does_not_fail_if_directory_exists(self, tmp_path) -> None:
        """Test that function succeeds when directory already exists."""
        history_path = anyio.Path(tmp_path) / "history.txt"
        await history_path.parent.mkdir(parents=True, exist_ok=True)

        # Should not raise
        await _ensure_history_dir(history_path)

        assert await history_path.parent.exists()

    @pytest.mark.asyncio
    async def test_creates_nested_directories(self, tmp_path) -> None:
        """Test that nested directories are created."""
        history_path = anyio.Path(tmp_path) / "a" / "b" / "c" / "history.txt"

        await _ensure_history_dir(history_path)

        assert await history_path.parent.exists()
