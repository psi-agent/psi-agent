"""Tests for Telegram CLI."""

from __future__ import annotations

from psi_agent.channel.telegram.cli import Telegram


def test_telegram_cli_without_proxy():
    """Test Telegram CLI without proxy argument."""
    cli = Telegram(token="test-token", session_socket="/tmp/test.sock")

    assert cli.token == "test-token"
    assert cli.session_socket == "/tmp/test.sock"
    assert cli.proxy is None


def test_telegram_cli_with_proxy():
    """Test Telegram CLI with proxy argument."""
    cli = Telegram(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="socks5://localhost:1080",
    )

    assert cli.token == "test-token"
    assert cli.session_socket == "/tmp/test.sock"
    assert cli.proxy == "socks5://localhost:1080"


def test_telegram_cli_with_http_proxy():
    """Test Telegram CLI with HTTP proxy."""
    cli = Telegram(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="http://proxy.example.com:8080",
    )

    assert cli.proxy == "http://proxy.example.com:8080"


def test_telegram_cli_with_https_proxy():
    """Test Telegram CLI with HTTPS proxy."""
    cli = Telegram(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="https://proxy.example.com:8443",
    )

    assert cli.proxy == "https://proxy.example.com:8443"


def test_telegram_cli_with_proxy_auth():
    """Test Telegram CLI with proxy containing credentials."""
    cli = Telegram(
        token="test-token",
        session_socket="/tmp/test.sock",
        proxy="socks5://user:password@proxy.example.com:1080",
    )

    assert cli.proxy == "socks5://user:password@proxy.example.com:1080"
