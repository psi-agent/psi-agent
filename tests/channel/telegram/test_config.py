"""Tests for TelegramConfig."""

from __future__ import annotations

from pathlib import Path

from psi_agent.channel.telegram.config import TelegramConfig


def test_telegram_config_creation():
    """Test TelegramConfig can be created with required fields."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    assert config.token == "test-token"
    assert config.session_socket == "/tmp/test.sock"


def test_telegram_config_socket_path():
    """Test socket_path returns Path object."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    result = config.socket_path()

    assert isinstance(result, Path)
    assert result == Path("/tmp/test.sock")
