"""Tests for Anthropic Messages CLI module."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.ai.anthropic_messages.cli import AnthropicMessages, main
from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig


class TestAnthropicMessagesCli:
    """Tests for Anthropic Messages CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
        )
        assert cli.session_socket == "/tmp/test.sock"
        assert cli.model == "claude-3-opus"
        assert cli.api_key == "test-key"
        assert cli.base_url == "https://api.anthropic.com"  # default
        assert cli.max_tokens == 4096  # default

    def test_cli_with_custom_options(self) -> None:
        """Test CLI with custom options."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-sonnet",
            api_key="test-key",
            base_url="https://custom.api.com",
            max_tokens=8192,
        )
        assert cli.base_url == "https://custom.api.com"
        assert cli.max_tokens == 8192

    def test_cli_config_creation(self) -> None:
        """Test CLI creates valid config."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
        )

        # Verify config can be created from CLI args
        config = AnthropicMessagesConfig(
            session_socket=cli.session_socket,
            model=cli.model,
            api_key=cli.api_key,
            base_url=cli.base_url,
            max_tokens=cli.max_tokens,
        )
        assert config.session_socket == "/tmp/test.sock"
        assert config.model == "claude-3-opus"


class TestAnthropicMessagesMain:
    """Tests for main function."""

    def test_main_exists(self) -> None:
        """Test main function exists and is callable."""
        assert callable(main)

    def test_main_is_function(self) -> None:
        """Test main is a function."""
        import inspect

        assert inspect.isfunction(main)

    @patch("psi_agent.ai.anthropic_messages.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main function calls tyro.cli."""
        main()
        mock_cli.assert_called_once_with(AnthropicMessages)


class TestAnthropicMessagesDefaults:
    """Tests for default values."""

    def test_default_base_url(self) -> None:
        """Test default base URL is set correctly."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
        )
        assert cli.base_url == "https://api.anthropic.com"

    def test_default_max_tokens(self) -> None:
        """Test default max_tokens is set correctly."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
        )
        assert cli.max_tokens == 4096


class TestAnthropicMessagesModelVariants:
    """Tests for different model variants."""

    def test_claude_3_opus(self) -> None:
        """Test CLI with Claude 3 Opus model."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus-20240229",
            api_key="test-key",
        )
        assert cli.model == "claude-3-opus-20240229"

    def test_claude_3_sonnet(self) -> None:
        """Test CLI with Claude 3 Sonnet model."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-sonnet-20240229",
            api_key="test-key",
        )
        assert cli.model == "claude-3-sonnet-20240229"

    def test_claude_3_haiku(self) -> None:
        """Test CLI with Claude 3 Haiku model."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-haiku-20240307",
            api_key="test-key",
        )
        assert cli.model == "claude-3-haiku-20240307"


class TestAnthropicMessagesCall:
    """Tests for CLI __call__ method."""

    @patch("psi_agent.ai.anthropic_messages.cli.mask_sensitive_args")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesServer")
    @patch("psi_agent.ai.anthropic_messages.cli.asyncio.run")
    def test_cli_call_masks_sensitive_args(
        self, mock_run: MagicMock, mock_server: MagicMock, mock_mask: MagicMock
    ) -> None:
        """Test CLI __call__ masks sensitive arguments."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="secret-key",
        )
        cli()

        mock_mask.assert_called_once_with(["api_key"])

    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesServer")
    @patch("psi_agent.ai.anthropic_messages.cli.asyncio.run")
    def test_cli_call_creates_server(
        self, mock_run: MagicMock, mock_server_class: MagicMock
    ) -> None:
        """Test CLI __call__ creates server with correct config."""
        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
            base_url="https://custom.api.com",
            max_tokens=8192,
        )
        cli()

        mock_server_class.assert_called_once()
        call_args = mock_server_class.call_args
        config = call_args[0][0]
        assert isinstance(config, AnthropicMessagesConfig)
        assert config.session_socket == "/tmp/test.sock"
        assert config.model == "claude-3-opus"
        assert config.api_key == "test-key"
        assert config.base_url == "https://custom.api.com"
        assert config.max_tokens == 8192

    def test_cli_call_runs_async_loop(self) -> None:
        """Test CLI __call__ runs the async event loop."""
        call_count = [0]

        def mock_run(coro):
            call_count[0] += 1

        with (
            patch.object(asyncio, "run", side_effect=mock_run),
            patch("psi_agent.ai.anthropic_messages.cli.mask_sensitive_args"),
            patch(
                "psi_agent.ai.anthropic_messages.cli.AnthropicMessagesServer"
            ) as mock_server_class,
        ):
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server

            cli = AnthropicMessages(
                session_socket="/tmp/test.sock",
                model="claude-3-opus",
                api_key="test-key",
            )
            cli()

        assert call_count[0] == 1
