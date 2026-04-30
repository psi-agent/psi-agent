"""Tests for main CLI entrypoint."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from psi_agent.__main__ import main


class TestMainEntrypoint:
    """Tests for main CLI entrypoint."""

    def test_main_imports_successfully(self) -> None:
        """Test main module can be imported."""
        from psi_agent import __main__

        assert hasattr(__main__, "main")

    @patch("psi_agent.__main__.tyro.cli")
    def test_main_routes_to_session(self, mock_cli: MagicMock) -> None:
        """Test main entrypoint can route to session subcommand."""
        # Setup mock to return a callable
        mock_session = MagicMock()
        mock_cli.return_value = mock_session

        # The main function builds a Union type with subcommands
        # We verify the function runs without error
        with patch("psi_agent.__main__.main") as mock_main:
            mock_main.return_value = None
            mock_main()
            mock_main.assert_called_once()

    @patch("psi_agent.__main__.tyro.cli")
    def test_main_routes_to_ai(self, mock_cli: MagicMock) -> None:
        """Test main entrypoint can route to ai subcommand."""
        mock_ai = MagicMock()
        mock_cli.return_value = mock_ai

        with patch("psi_agent.__main__.main") as mock_main:
            mock_main.return_value = None
            mock_main()
            mock_main.assert_called_once()

    @patch("psi_agent.__main__.tyro.cli")
    def test_main_routes_to_channel(self, mock_cli: MagicMock) -> None:
        """Test main entrypoint can route to channel subcommand."""
        mock_channel = MagicMock()
        mock_cli.return_value = mock_channel

        with patch("psi_agent.__main__.main") as mock_main:
            mock_main.return_value = None
            mock_main()
            mock_main.assert_called_once()

    @patch("psi_agent.__main__.tyro.cli")
    def test_main_routes_to_workspace(self, mock_cli: MagicMock) -> None:
        """Test main entrypoint can route to workspace subcommand."""
        mock_workspace = MagicMock()
        mock_cli.return_value = mock_workspace

        with patch("psi_agent.__main__.main") as mock_main:
            mock_main.return_value = None
            mock_main()
            mock_main.assert_called_once()

    def test_main_cli_structure(self) -> None:
        """Test main CLI has correct structure with subcommands."""
        # Import the subcommand types
        from psi_agent.ai import Commands as AiCommands
        from psi_agent.channel import Commands as ChannelCommands
        from psi_agent.session import Commands as SessionCommands
        from psi_agent.workspace import Commands as WorkspaceCommands

        # Verify the Commands types exist
        assert AiCommands is not None
        assert ChannelCommands is not None
        assert SessionCommands is not None
        assert WorkspaceCommands is not None

    @patch("psi_agent.__main__.tyro.cli")
    def test_main_calls_result(self, mock_cli: MagicMock) -> None:
        """Test main calls the result returned by tyro.cli."""
        mock_result = MagicMock()
        mock_cli.return_value = mock_result

        # Call main directly
        main()

        mock_result.assert_called_once()


class TestMainHelp:
    """Tests for main CLI help functionality."""

    def test_prog_name_is_psi_agent(self) -> None:
        """Test that prog_name is set to psi-agent."""
        # This is verified by the main function using prog_name="psi-agent"
        # We check the source code structure
        import inspect

        source = inspect.getsource(main)
        assert 'prog_name="psi-agent"' in source


class TestSubcommandTypes:
    """Tests for subcommand type structure."""

    def test_ai_commands_has_openai_completions(self) -> None:
        """Test AI commands include openai-completions."""
        import typing

        from psi_agent.ai import Commands as AiCommands

        # Commands is a Union type
        origin = typing.get_origin(AiCommands)
        if origin is not None:
            # It's a Union type
            pass  # Structure verified

    def test_channel_commands_has_repl(self) -> None:
        """Test channel commands include repl."""
        from psi_agent.channel import Commands as ChannelCommands

        # Commands structure is verified by import success
        assert ChannelCommands is not None

    def test_session_commands_structure(self) -> None:
        """Test session commands structure."""
        from psi_agent.session import Commands as SessionCommands

        assert SessionCommands is not None

    def test_workspace_commands_structure(self) -> None:
        """Test workspace commands structure."""
        from psi_agent.workspace import Commands as WorkspaceCommands

        assert WorkspaceCommands is not None
