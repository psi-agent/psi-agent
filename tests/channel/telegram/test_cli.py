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


def test_telegram_cli_streaming_defaults():
    """Test Telegram CLI streaming defaults to enabled."""
    cli = Telegram(token="test-token", session_socket="/tmp/test.sock")

    assert cli.no_stream is False
    assert cli.stream_interval == 1.0


def test_telegram_cli_no_stream_flag():
    """Test Telegram CLI with --no-stream flag."""
    cli = Telegram(token="test-token", session_socket="/tmp/test.sock", no_stream=True)

    assert cli.no_stream is True


def test_telegram_cli_custom_stream_interval():
    """Test Telegram CLI with custom stream interval."""
    cli = Telegram(token="test-token", session_socket="/tmp/test.sock", stream_interval=0.5)

    assert cli.stream_interval == 0.5


def test_telegram_cli_main():
    """Test main entry point creates CLI."""
    from psi_agent.channel.telegram.cli import main

    # Just verify it's callable
    assert callable(main)
