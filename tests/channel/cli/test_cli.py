"""Tests for channel CLI module."""

from __future__ import annotations

import pytest

from psi_agent.channel.cli.cli import Cli
from psi_agent.channel.cli.client import CliClient
from psi_agent.channel.cli.config import CliConfig


class TestCliConfig:
    """Tests for CLI config."""

    def test_config_creation(self) -> None:
        """Test config can be created."""
        config = CliConfig(session_socket="/tmp/test.sock")
        assert config.session_socket == "/tmp/test.sock"
        assert config.stream is True

    def test_config_with_stream_false(self) -> None:
        """Test config with stream=False."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        assert config.stream is False

    def test_socket_path(self) -> None:
        """Test socket_path returns anyio.Path."""
        import anyio

        config = CliConfig(session_socket="/tmp/test.sock")
        path = config.socket_path()
        assert isinstance(path, anyio.Path)


class TestCliClient:
    """Tests for CLI client."""

    def test_client_creation(self) -> None:
        """Test client can be created."""
        config = CliConfig(session_socket="/tmp/test.sock")
        client = CliClient(config)
        assert client.config is config
        assert client._session is None
        assert client._connector is None


class TestCliFlags:
    """Tests for CLI flag handling."""

    def test_cli_default_stream_enabled(self) -> None:
        """Test CLI defaults to streaming enabled."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello")

        assert cli.stream is True

    def test_cli_no_stream_flag(self) -> None:
        """Test CLI --no-stream flag disables streaming."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=False)

        assert cli.stream is False

    def test_cli_session_socket(self) -> None:
        """Test CLI session_socket attribute."""
        cli = Cli(session_socket="/tmp/test.sock", message="Hello")

        assert cli.session_socket == "/tmp/test.sock"

    def test_cli_message(self) -> None:
        """Test CLI message attribute."""
        cli = Cli(session_socket="/tmp/test.sock", message="Test message")

        assert cli.message == "Test message"


class TestCliMain:
    """Tests for CLI main function."""

    def test_main_exists(self) -> None:
        """Test main function exists."""
        from psi_agent.channel.cli.cli import main

        assert callable(main)
