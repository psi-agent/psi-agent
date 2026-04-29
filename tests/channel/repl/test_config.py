"""Tests for REPL channel config."""

from __future__ import annotations

import anyio
import platformdirs

from psi_agent.channel.repl.config import ReplConfig


class TestReplConfig:
    """Tests for ReplConfig."""

    def test_config_creation(self) -> None:
        """Test creating config with required fields."""
        config = ReplConfig(session_socket="/tmp/test.sock")

        assert config.session_socket == "/tmp/test.sock"

    def test_socket_path(self) -> None:
        """Test socket_path returns anyio.Path object."""
        config = ReplConfig(session_socket="/tmp/test.sock")

        assert isinstance(config.socket_path(), anyio.Path)
        assert config.socket_path() == anyio.Path("/tmp/test.sock")

    def test_get_history_path_default(self) -> None:
        """Test get_history_path returns default path when not configured."""
        config = ReplConfig(session_socket="/tmp/test.sock")

        expected = anyio.Path(platformdirs.user_cache_dir("psi-agent")) / "repl_history.txt"
        assert config.get_history_path() == expected

    def test_get_history_path_custom(self) -> None:
        """Test get_history_path returns custom path when configured."""
        config = ReplConfig(session_socket="/tmp/test.sock", history_file="/custom/history.txt")

        assert config.get_history_path() == anyio.Path("/custom/history.txt")

    def test_history_file_default_none(self) -> None:
        """Test history_file defaults to None."""
        config = ReplConfig(session_socket="/tmp/test.sock")

        assert config.history_file is None
