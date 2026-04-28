"""Tests for REPL interface."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from prompt_toolkit.history import InMemoryHistory

from psi_agent.channel.repl.config import ReplConfig
from psi_agent.channel.repl.repl import Repl


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
    async def test_quit_command(self, repl: Repl) -> None:
        """Test /quit command exits REPL."""
        inputs = ["/quit"]
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with patch.object(repl, "_read_input", mock_read), patch("builtins.print") as mock_print:
            await repl.run()

            # Check goodbye message was printed
            assert any("Goodbye" in str(call) for call in mock_print.call_args_list)

    @pytest.mark.asyncio
    async def test_empty_input_ignored(self, repl: Repl) -> None:
        """Test empty input is ignored."""
        inputs = ["", "/quit"]
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
        inputs = ["Hello", "/quit"]
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        mock_send = AsyncMock(return_value="Hi there!")
        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", mock_send),
            patch("builtins.print"),
        ):
            await repl.run()

            # send_message should be called with the user input
            mock_send.assert_called_once_with("Hello")


class TestReplHistory:
    """Tests for REPL history navigation."""

    @pytest.fixture
    def config(self) -> ReplConfig:
        """Create test config."""
        return ReplConfig(session_socket="/tmp/test.sock")

    @pytest.fixture
    def repl(self, config: ReplConfig) -> Repl:
        """Create test REPL."""
        return Repl(config)

    @pytest.mark.asyncio
    async def test_history_stored_in_session(self, repl: Repl) -> None:
        """Test that inputs are stored in prompt-toolkit history."""
        inputs = ["First message", "Second message", "/quit"]
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", AsyncMock(return_value="Response")),
            patch("builtins.print"),
        ):
            await repl.run()

            # Session should have InMemoryHistory
            assert repl._session is not None
            assert isinstance(repl._session.history, InMemoryHistory)

    @pytest.mark.asyncio
    async def test_multiline_input_preserved(self, repl: Repl) -> None:
        """Test multiline input is preserved with line breaks."""
        multiline_input = "Line 1\nLine 2\nLine 3"
        inputs = [multiline_input, "/quit"]
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

            # Check multiline message preserved
            mock_send.assert_called_once_with(multiline_input)


class TestReplEditing:
    """Tests for REPL line editing capabilities."""

    @pytest.fixture
    def config(self) -> ReplConfig:
        """Create test config."""
        return ReplConfig(session_socket="/tmp/test.sock")

    @pytest.fixture
    def repl(self, config: ReplConfig) -> Repl:
        """Create test REPL."""
        return Repl(config)

    @pytest.mark.asyncio
    async def test_prompt_session_created(self, repl: Repl) -> None:
        """Test that PromptSession is created during run."""
        inputs = ["/quit"]
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
        repl._session.history = InMemoryHistory()

        _ = await repl._read_input()

        # Verify prompt_async was called
        repl._session.prompt_async.assert_called_once()
        call_args = repl._session.prompt_async.call_args
        assert call_args[0][0] == "> "  # prompt string
        assert call_args[1]["multiline"] is True  # multiline enabled
