"""Tests for session/config.py — SessionConfig."""

from __future__ import annotations

import anyio

from psi_agent.session.config import SessionConfig


class TestSessionConfigConstruction:
    """Tests for SessionConfig construction."""

    def test_default_construction(self) -> None:
        config = SessionConfig(
            workspace="/tmp/ws",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
        )
        assert config.workspace == "/tmp/ws"
        assert config.channel_socket == "/tmp/channel.sock"
        assert config.ai_socket == "/tmp/ai.sock"
        assert config.history_file is None

    def test_construction_with_history_file(self) -> None:
        config = SessionConfig(
            workspace="/tmp/ws",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            history_file="/tmp/hist.json",
        )
        assert config.history_file == "/tmp/hist.json"


class TestSessionConfigHelperMethods:
    """Tests for SessionConfig helper methods."""

    def setup_method(self) -> None:
        self.config = SessionConfig(
            workspace="/tmp/ws",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
        )

    def test_channel_socket_path(self) -> None:
        result = self.config.channel_socket_path()
        assert isinstance(result, anyio.Path)
        assert str(result) == "/tmp/channel.sock"

    def test_ai_socket_path(self) -> None:
        result = self.config.ai_socket_path()
        assert isinstance(result, anyio.Path)
        assert str(result) == "/tmp/ai.sock"

    def test_workspace_path(self) -> None:
        result = self.config.workspace_path()
        assert isinstance(result, anyio.Path)
        assert str(result) == "/tmp/ws"

    def test_history_file_path_none(self) -> None:
        assert self.config.history_file_path() is None

    def test_history_file_path_non_none(self) -> None:
        config = SessionConfig(
            workspace="/tmp/ws",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
            history_file="/tmp/hist.json",
        )
        result = config.history_file_path()
        assert isinstance(result, anyio.Path)
        assert str(result) == "/tmp/hist.json"

    def test_tools_dir(self) -> None:
        result = self.config.tools_dir()
        assert isinstance(result, anyio.Path)
        assert str(result) == "/tmp/ws/tools"

    def test_systems_dir(self) -> None:
        result = self.config.systems_dir()
        assert isinstance(result, anyio.Path)
        assert str(result) == "/tmp/ws/systems"


class TestSessionConfigCornerCases:
    """Corner case tests for SessionConfig."""

    def test_workspace_with_spaces(self) -> None:
        config = SessionConfig(
            workspace="/tmp/my workspace",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
        )
        assert str(config.tools_dir()) == "/tmp/my workspace/tools"

    def test_workspace_with_unicode(self) -> None:
        config = SessionConfig(
            workspace="/tmp/工作区",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
        )
        assert str(config.tools_dir()) == "/tmp/工作区/tools"

    def test_workspace_with_trailing_slash(self) -> None:
        config = SessionConfig(
            workspace="/tmp/ws/",
            channel_socket="/tmp/channel.sock",
            ai_socket="/tmp/ai.sock",
        )
        assert str(config.tools_dir()) == "/tmp/ws/tools"
