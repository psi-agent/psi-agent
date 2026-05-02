"""Tests for Telegram CLI."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.channel.telegram.cli import Telegram, main


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

    assert cli.stream is True
    assert cli.stream_interval == 1.0


def test_telegram_cli_no_stream_flag():
    """Test Telegram CLI with --no-stream flag."""
    cli = Telegram(token="test-token", session_socket="/tmp/test.sock", stream=False)

    assert cli.stream is False


def test_telegram_cli_custom_stream_interval():
    """Test Telegram CLI with custom stream interval."""
    cli = Telegram(token="test-token", session_socket="/tmp/test.sock", stream_interval=0.5)

    assert cli.stream_interval == 0.5


def test_telegram_cli_main():
    """Test main entry point creates CLI."""
    from psi_agent.channel.telegram.cli import main

    # Just verify it's callable
    assert callable(main)


class TestTelegramCliCall:
    """Tests for Telegram CLI __call__ method."""

    @patch("psi_agent.channel.telegram.cli.asyncio.run")
    @patch("psi_agent.channel.telegram.cli.TelegramBot")
    @patch("psi_agent.channel.telegram.cli.TelegramConfig")
    def test_cli_call_creates_config(
        self,
        mock_config_cls: MagicMock,
        mock_bot_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ creates config with correct parameters."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_bot = MagicMock()
        mock_bot.start = AsyncMock()
        mock_bot_cls.return_value = mock_bot

        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="http://localhost:8080",
            stream=False,
            stream_interval=0.5,
        )
        cli()

        mock_config_cls.assert_called_once_with(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="http://localhost:8080",
            stream=False,
            stream_interval=0.5,
        )

    @patch("psi_agent.channel.telegram.cli.asyncio.run")
    @patch("psi_agent.channel.telegram.cli.TelegramBot")
    @patch("psi_agent.channel.telegram.cli.TelegramConfig")
    def test_cli_call_creates_bot(
        self,
        mock_config_cls: MagicMock,
        mock_bot_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ creates bot with config."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_bot = MagicMock()
        mock_bot.start = AsyncMock()
        mock_bot_cls.return_value = mock_bot

        cli = Telegram(token="test-token", session_socket="/tmp/test.sock")
        cli()

        mock_bot_cls.assert_called_once_with(mock_config)

    @patch("psi_agent.channel.telegram.cli.asyncio.run")
    @patch("psi_agent.channel.telegram.cli.TelegramBot")
    @patch("psi_agent.channel.telegram.cli.TelegramConfig")
    def test_cli_call_starts_bot(
        self,
        mock_config_cls: MagicMock,
        mock_bot_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ starts the bot."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_bot = MagicMock()
        mock_bot.start = AsyncMock()
        mock_bot_cls.return_value = mock_bot

        cli = Telegram(token="test-token", session_socket="/tmp/test.sock")
        cli()

        mock_bot.start.assert_called_once()


class TestTelegramMain:
    """Tests for Telegram CLI main function."""

    @patch("psi_agent.channel.telegram.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main calls tyro.cli."""
        main()
        mock_cli.assert_called_once_with(Telegram)
