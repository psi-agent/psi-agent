"""Tests for REPL channel config."""

from pathlib import Path

from psi_agent.channel.repl.config import ReplConfig


class TestReplConfig:
    """Tests for ReplConfig."""

    def test_config_creation(self) -> None:
        """Test creating config with required fields."""
        config = ReplConfig(session_socket="/tmp/test.sock")

        assert config.session_socket == "/tmp/test.sock"

    def test_socket_path(self) -> None:
        """Test socket_path returns Path object."""
        config = ReplConfig(session_socket="/tmp/test.sock")

        assert isinstance(config.socket_path(), Path)
        assert config.socket_path() == Path("/tmp/test.sock")
