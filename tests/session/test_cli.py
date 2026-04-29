"""Tests for session CLI module."""

from __future__ import annotations

from psi_agent.session.cli import Session
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
