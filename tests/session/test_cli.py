"""Tests for session CLI module."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.session.cli import Session, main
from psi_agent.session.config import SessionConfig


class TestSessionCli:
    """Tests for session CLI dataclass."""

    def test_session_import(self) -> None:
        """Test Session class can be imported."""
        # Test instantiation
        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )
        assert session.channel_socket == "/tmp/channel.sock"
        assert session.ai_socket == "/tmp/ai.sock"
        assert session.workspace == "/tmp/workspace"
        assert session.history_file is None  # default

    def test_session_with_history_file(self) -> None:
        """Test Session with history file option."""
        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            history_file="/tmp/history.json",
        )
        assert session.history_file == "/tmp/history.json"

    def test_session_config_creation(self) -> None:
        """Test Session creates valid config."""
        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )

        # Verify config can be created from CLI args
        config = SessionConfig(
            channel_socket=session.channel_socket,
            ai_socket=session.ai_socket,
            workspace=session.workspace,
            history_file=session.history_file,
        )
        assert config.channel_socket == "/tmp/channel.sock"
        assert config.ai_socket == "/tmp/ai.sock"

    def test_session_with_reasoning_effort(self) -> None:
        """Test Session with reasoning_effort option."""
        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            reasoning_effort="high",
        )
        assert session.reasoning_effort == "high"

    def test_session_default_reasoning_effort(self) -> None:
        """Test default reasoning_effort is medium."""
        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )
        assert session.reasoning_effort == "medium"


class TestSessionMain:
    """Tests for main function."""

    def test_main_exists(self) -> None:
        """Test main function exists and is callable."""
        assert callable(main)

    def test_main_is_function(self) -> None:
        """Test main is a function."""
        import inspect

        assert inspect.isfunction(main)

    @patch("psi_agent.session.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main function calls tyro.cli."""
        main()
        mock_cli.assert_called_once_with(Session)


class TestSessionDefaults:
    """Tests for default values."""

    def test_default_history_file(self) -> None:
        """Test default history_file is None."""
        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )
        assert session.history_file is None


class TestSessionPaths:
    """Tests for various path configurations."""

    def test_relative_paths(self) -> None:
        """Test Session with relative paths."""
        session = Session(
            channel_socket="./channel.sock",
            ai_socket="./ai.sock",
            workspace="./workspace",
        )
        assert session.channel_socket == "./channel.sock"
        assert session.ai_socket == "./ai.sock"
        assert session.workspace == "./workspace"

    def test_absolute_paths(self) -> None:
        """Test Session with absolute paths."""
        session = Session(
            channel_socket="/var/run/psi/channel.sock",
            ai_socket="/var/run/psi/ai.sock",
            workspace="/home/user/workspace",
        )
        assert session.channel_socket == "/var/run/psi/channel.sock"
        assert session.ai_socket == "/var/run/psi/ai.sock"
        assert session.workspace == "/home/user/workspace"


class TestSessionCall:
    """Tests for Session __call__ method."""

    @patch("psi_agent.session.cli.SessionServer")
    @patch("psi_agent.session.cli.asyncio.run")
    def test_cli_call_creates_server(
        self, mock_run: MagicMock, mock_server_class: MagicMock
    ) -> None:
        """Test CLI __call__ creates server with correct config."""
        cli = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )
        cli()

        mock_server_class.assert_called_once()
        call_args = mock_server_class.call_args
        config = call_args[0][0]
        assert isinstance(config, SessionConfig)
        assert config.channel_socket == "/tmp/channel.sock"
        assert config.ai_socket == "/tmp/ai.sock"

    @patch("psi_agent.session.cli.SessionServer")
    @patch("psi_agent.session.cli.asyncio.run")
    def test_cli_call_with_history_file(
        self, mock_run: MagicMock, mock_server_class: MagicMock
    ) -> None:
        """Test CLI __call__ with history file."""
        cli = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            history_file="/tmp/history.json",
        )
        cli()

        call_args = mock_server_class.call_args
        config = call_args[0][0]
        assert config.history_file == "/tmp/history.json"

    @patch("psi_agent.session.cli.SessionServer")
    @patch("psi_agent.session.cli.asyncio.run")
    def test_cli_call_with_reasoning_effort(
        self, mock_run: MagicMock, mock_server_class: MagicMock
    ) -> None:
        """Test CLI __call__ with reasoning effort."""
        cli = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            reasoning_effort="high",
        )
        cli()

        call_args = mock_server_class.call_args
        config = call_args[0][0]
        assert config.reasoning_effort == "high"

    def test_cli_call_runs_async_loop(self) -> None:
        """Test CLI __call__ runs the async event loop."""
        call_count = [0]

        def mock_run(coro):
            call_count[0] += 1

        with (
            patch.object(asyncio, "run", side_effect=mock_run),
            patch("psi_agent.session.cli.SessionServer") as mock_server_class,
        ):
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server

            cli = Session(
                channel_socket="/tmp/channel.sock",
                ai_socket="/tmp/ai.sock",
                workspace="/tmp/workspace",
            )
            cli()

        assert call_count[0] == 1
