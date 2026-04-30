"""Tests for REPL channel CLI module."""

from __future__ import annotations

from psi_agent.channel.repl.cli import Repl, main
from psi_agent.channel.repl.config import ReplConfig


class TestReplCli:
    """Tests for REPL CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        cli = Repl(session_socket="/tmp/test.sock")
        assert cli.session_socket == "/tmp/test.sock"
        assert cli.no_stream is False  # default

    def test_cli_with_no_stream(self) -> None:
        """Test CLI with no_stream option."""
        cli = Repl(
            session_socket="/tmp/test.sock",
            no_stream=True,
        )
        assert cli.no_stream is True

    def test_cli_config_creation(self) -> None:
        """Test CLI creates valid config."""
        cli = Repl(
            session_socket="/tmp/test.sock",
            no_stream=False,
        )

        # Verify config can be created from CLI args
        config = ReplConfig(
            session_socket=cli.session_socket,
            stream=not cli.no_stream,
        )
        assert config.session_socket == "/tmp/test.sock"
        assert config.stream is True


class TestReplMain:
    """Tests for main function."""

    def test_main_exists(self) -> None:
        """Test main function exists and is callable."""
        assert callable(main)

    def test_main_is_function(self) -> None:
        """Test main is a function."""
        import inspect

        assert inspect.isfunction(main)


class TestReplDefaults:
    """Tests for default values."""

    def test_default_no_stream(self) -> None:
        """Test default no_stream is False."""
        cli = Repl(session_socket="/tmp/test.sock")
        assert cli.no_stream is False


class TestReplSocketPaths:
    """Tests for various socket path configurations."""

    def test_relative_socket_path(self) -> None:
        """Test CLI with relative socket path."""
        cli = Repl(session_socket="./session.sock")
        assert cli.session_socket == "./session.sock"

    def test_absolute_socket_path(self) -> None:
        """Test CLI with absolute socket path."""
        cli = Repl(session_socket="/var/run/psi/session.sock")
        assert cli.session_socket == "/var/run/psi/session.sock"

    def test_tmp_socket_path(self) -> None:
        """Test CLI with /tmp socket path."""
        cli = Repl(session_socket="/tmp/psi-session.sock")
        assert cli.session_socket == "/tmp/psi-session.sock"
