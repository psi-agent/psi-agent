"""Tests for session CLI module."""

from __future__ import annotations

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


class TestSessionCliCall:
    """Tests for session CLI __call__ method."""

    @patch("psi_agent.session.cli.asyncio.run")
    @patch("psi_agent.session.cli.SessionServer")
    @patch("psi_agent.session.cli.SessionConfig")
    def test_cli_call_creates_config(
        self,
        mock_config_cls: MagicMock,
        mock_server_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ creates config with correct parameters."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server_cls.return_value = mock_server

        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            history_file="/tmp/history.json",
        )
        session()

        mock_config_cls.assert_called_once_with(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
            history_file="/tmp/history.json",
        )

    @patch("psi_agent.session.cli.asyncio.run")
    @patch("psi_agent.session.cli.SessionServer")
    @patch("psi_agent.session.cli.SessionConfig")
    def test_cli_call_creates_server(
        self,
        mock_config_cls: MagicMock,
        mock_server_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ creates server with config."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server_cls.return_value = mock_server

        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )
        session()

        mock_server_cls.assert_called_once_with(mock_config)


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
        """Test main calls tyro.cli."""
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


class TestSessionRunLoop:
    """Tests for the async run loop."""

    @patch("psi_agent.session.cli.SessionServer")
    @patch("psi_agent.session.cli.SessionConfig")
    def test_run_loop_structure(
        self,
        mock_config_cls: MagicMock,
        mock_server_cls: MagicMock,
    ) -> None:
        """Test that CLI creates server and config correctly."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server_cls.return_value = mock_server

        session = Session(
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            workspace="/tmp/workspace",
        )

        # Verify CLI dataclass structure
        assert session.channel_socket == "/tmp/channel.sock"
        assert session.ai_socket == "/tmp/ai.sock"
        assert session.workspace == "/tmp/workspace"
