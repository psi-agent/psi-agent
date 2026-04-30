"""Tests for TelegramConfig."""

from __future__ import annotations

import anyio

from psi_agent.channel.telegram.config import TelegramConfig


def test_telegram_config_creation():
    """Test TelegramConfig can be created with required fields."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    assert config.token == "test-token"
    assert config.session_socket == "/tmp/test.sock"


def test_telegram_config_socket_path():
    """Test socket_path returns anyio.Path object."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    result = config.socket_path()

    assert isinstance(result, anyio.Path)
    assert result == anyio.Path("/tmp/test.sock")


def test_telegram_config_proxy_default_none():
    """Test TelegramConfig proxy defaults to None."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    assert config.proxy is None


def test_telegram_config_with_proxy():
    """Test TelegramConfig can be created with proxy."""
    config = TelegramConfig(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="socks5://localhost:1080",
    )

    assert config.proxy == "socks5://localhost:1080"


def test_telegram_config_with_http_proxy():
    """Test TelegramConfig with HTTP proxy."""
    config = TelegramConfig(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="http://proxy.example.com:8080",
    )

    assert config.proxy == "http://proxy.example.com:8080"


def test_telegram_config_with_proxy_auth():
    """Test TelegramConfig with proxy containing credentials."""
    config = TelegramConfig(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="socks5://user:password@proxy.example.com:1080",
    )

    assert config.proxy == "socks5://user:password@proxy.example.com:1080"


def test_telegram_config_stream_default_true():
    """Test TelegramConfig stream defaults to True."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    assert config.stream is True


def test_telegram_config_stream_interval_default():
    """Test TelegramConfig stream_interval defaults to 1.0."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock")

    assert config.stream_interval == 1.0


def test_telegram_config_with_stream_disabled():
    """Test TelegramConfig can be created with stream disabled."""
    config = TelegramConfig(token="test-token", session_socket="/tmp/test.sock", stream=False)

    assert config.stream is False


def test_telegram_config_with_custom_stream_interval():
    """Test TelegramConfig can be created with custom stream_interval."""
    config = TelegramConfig(
        token="test-token", session_socket="/tmp/test.sock", stream_interval=0.5
    )

    assert config.stream_interval == 0.5
