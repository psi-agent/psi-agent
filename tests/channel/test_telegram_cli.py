"""Tests for Telegram channel CLI module."""

from __future__ import annotations

from psi_agent.channel.telegram.cli import Telegram, main
from psi_agent.channel.telegram.config import TelegramConfig


class TestTelegramCli:
    """Tests for Telegram CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
        )
        assert cli.token == "test-token"
        assert cli.session_socket == "/tmp/test.sock"
        assert cli.proxy is None  # default
        assert cli.stream is True  # default
        assert cli.stream_interval == 1.0  # default

    def test_cli_with_proxy(self) -> None:
        """Test CLI with proxy option."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://localhost:1080",
        )
        assert cli.proxy == "socks5://localhost:1080"

    def test_cli_with_no_stream(self) -> None:
        """Test CLI with stream=False option."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            stream=False,
        )
        assert cli.stream is False

    def test_cli_with_stream_interval(self) -> None:
        """Test CLI with custom stream_interval."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            stream_interval=0.5,
        )
        assert cli.stream_interval == 0.5

    def test_cli_config_creation(self) -> None:
        """Test CLI creates valid config."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy=None,
            stream=True,
            stream_interval=1.0,
        )

        # Verify config can be created from CLI args
        config = TelegramConfig(
            token=cli.token,
            session_socket=cli.session_socket,
            proxy=cli.proxy,
            stream=cli.stream,
            stream_interval=cli.stream_interval,
        )
        assert config.token == "test-token"
        assert config.session_socket == "/tmp/test.sock"
        assert config.stream is True


class TestTelegramMain:
    """Tests for main function."""

    def test_main_exists(self) -> None:
        """Test main function exists and is callable."""
        assert callable(main)

    def test_main_is_function(self) -> None:
        """Test main is a function."""
        import inspect

        assert inspect.isfunction(main)


class TestTelegramDefaults:
    """Tests for default values."""

    def test_default_proxy(self) -> None:
        """Test default proxy is None."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
        )
        assert cli.proxy is None

    def test_default_stream(self) -> None:
        """Test default stream is True."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
        )
        assert cli.stream is True

    def test_default_stream_interval(self) -> None:
        """Test default stream_interval is 1.0."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
        )
        assert cli.stream_interval == 1.0


class TestTelegramProxyFormats:
    """Tests for various proxy format configurations."""

    def test_socks5_proxy(self) -> None:
        """Test CLI with SOCKS5 proxy."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="socks5://user:pass@localhost:1080",
        )
        assert cli.proxy == "socks5://user:pass@localhost:1080"

    def test_http_proxy(self) -> None:
        """Test CLI with HTTP proxy."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="http://localhost:8080",
        )
        assert cli.proxy == "http://localhost:8080"

    def test_https_proxy(self) -> None:
        """Test CLI with HTTPS proxy."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            proxy="https://localhost:8443",
        )
        assert cli.proxy == "https://localhost:8443"


class TestTelegramStreamIntervals:
    """Tests for various stream interval configurations."""

    def test_fast_stream_interval(self) -> None:
        """Test CLI with fast stream interval."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            stream_interval=0.1,
        )
        assert cli.stream_interval == 0.1

    def test_slow_stream_interval(self) -> None:
        """Test CLI with slow stream interval."""
        cli = Telegram(
            token="test-token",
            session_socket="/tmp/test.sock",
            stream_interval=5.0,
        )
        assert cli.stream_interval == 5.0
