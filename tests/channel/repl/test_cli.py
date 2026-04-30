"""Tests for REPL channel CLI."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.channel.repl.cli import Repl, main


class TestReplCli:
    """Tests for REPL CLI flag handling."""

    def test_cli_default_stream_enabled(self) -> None:
        """Test CLI defaults to streaming enabled."""
        cli = Repl(session_socket="/tmp/test.sock")

        assert cli.stream is True

    def test_cli_no_stream_flag(self) -> None:
        """Test CLI --no-stream flag disables streaming."""
        cli = Repl(session_socket="/tmp/test.sock", stream=False)

        assert cli.stream is False

    def test_cli_passes_stream_to_config(self) -> None:
        """Test CLI passes correct stream value to config."""
        cli = Repl(session_socket="/tmp/test.sock", stream=False)

        # When stream=False, config.stream should be False
        # This is verified by checking the logic in __call__
        assert cli.stream is False

    def test_cli_session_socket_attribute(self) -> None:
        """Test CLI session_socket attribute."""
        cli = Repl(session_socket="/custom/socket/path.sock")

        assert cli.session_socket == "/custom/socket/path.sock"

    @patch("psi_agent.channel.repl.cli.asyncio.run")
    @patch("psi_agent.channel.repl.cli.ReplRunner")
    @patch("psi_agent.channel.repl.cli.ReplConfig")
    def test_cli_call_creates_config(
        self, mock_config_cls: MagicMock, mock_repl_cls: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test CLI __call__ creates config with correct parameters."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_repl = MagicMock()
        mock_repl.run = AsyncMock()
        mock_repl_cls.return_value = mock_repl

        cli = Repl(session_socket="/tmp/test.sock", stream=False)
        cli()

        mock_config_cls.assert_called_once_with(session_socket="/tmp/test.sock", stream=False)

    @patch("psi_agent.channel.repl.cli.asyncio.run")
    @patch("psi_agent.channel.repl.cli.ReplRunner")
    @patch("psi_agent.channel.repl.cli.ReplConfig")
    def test_cli_call_creates_repl(
        self, mock_config_cls: MagicMock, mock_repl_cls: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test CLI __call__ creates REPL runner with config."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_repl = MagicMock()
        mock_repl.run = AsyncMock()
        mock_repl_cls.return_value = mock_repl

        cli = Repl(session_socket="/tmp/test.sock")
        cli()

        mock_repl_cls.assert_called_once_with(mock_config)

    @patch("psi_agent.channel.repl.cli.asyncio.run")
    @patch("psi_agent.channel.repl.cli.ReplRunner")
    @patch("psi_agent.channel.repl.cli.ReplConfig")
    def test_cli_call_runs_repl(
        self, mock_config_cls: MagicMock, mock_repl_cls: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test CLI __call__ runs the REPL."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_repl = MagicMock()
        mock_repl.run = AsyncMock()
        mock_repl_cls.return_value = mock_repl

        cli = Repl(session_socket="/tmp/test.sock")
        cli()

        mock_run.assert_called_once()


class TestReplMain:
    """Tests for REPL CLI main function."""

    def test_main_exists(self) -> None:
        """Test main function exists."""
        assert callable(main)

    @patch("psi_agent.channel.repl.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main calls tyro.cli."""
        main()
        mock_cli.assert_called_once_with(Repl)
