"""Tests for REPL interface."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
        assert repl.history == []

    def test_repl_has_client(self, repl: Repl) -> None:
        """Test REPL has client."""
        assert repl.client is not None

    @pytest.mark.asyncio
    async def test_read_input(self, repl: Repl) -> None:
        """Test reading input from stdin."""
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop_instance = MagicMock()
            mock_loop_instance.run_in_executor = AsyncMock(return_value="Hello")
            mock_loop.return_value = mock_loop_instance

            result = await repl._read_input()
            assert result == "Hello"

    @pytest.mark.asyncio
    async def test_read_input_eof(self, repl: Repl) -> None:
        """Test reading input with EOF."""
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop_instance = MagicMock()
            mock_loop_instance.run_in_executor = AsyncMock(return_value=None)
            mock_loop.return_value = mock_loop_instance

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

        with patch.object(repl, "_read_input", mock_read), patch("builtins.print"):
            await repl.run()

            # History should not have empty message
            assert len(repl.history) == 0

    @pytest.mark.asyncio
    async def test_message_added_to_history(self, repl: Repl) -> None:
        """Test message is added to history."""
        inputs = ["Hello", "/quit"]
        input_iter = iter(inputs)

        async def mock_read() -> str | None:
            return next(input_iter, None)

        with (
            patch.object(repl, "_read_input", mock_read),
            patch.object(repl.client, "send_message", AsyncMock(return_value="Hi there!")),
            patch("builtins.print"),
        ):
            await repl.run()

            # Should have user and assistant messages
            assert len(repl.history) == 2
            assert repl.history[0]["role"] == "user"
            assert repl.history[0]["content"] == "Hello"
            assert repl.history[1]["role"] == "assistant"
            assert repl.history[1]["content"] == "Hi there!"
