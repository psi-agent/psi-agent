"""Tests for Anthropic Messages CLI module."""

from __future__ import annotations

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


class TestAnthropicMessagesCliCall:
    """Tests for Anthropic Messages CLI __call__ method."""

    @patch("psi_agent.ai.anthropic_messages.cli.asyncio.run")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesServer")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesConfig")
    @patch("psi_agent.ai.anthropic_messages.cli.mask_sensitive_args")
    def test_cli_call_masks_sensitive_args(
        self,
        mock_mask: MagicMock,
        mock_config_cls: MagicMock,
        mock_server_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ masks sensitive arguments."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server_cls.return_value = mock_server

        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
        )
        cli()

        mock_mask.assert_called_once_with(["api_key"])

    @patch("psi_agent.ai.anthropic_messages.cli.asyncio.run")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesServer")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesConfig")
    @patch("psi_agent.ai.anthropic_messages.cli.mask_sensitive_args")
    def test_cli_call_creates_config(
        self,
        mock_mask: MagicMock,
        mock_config_cls: MagicMock,
        mock_server_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ creates config with correct parameters."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server_cls.return_value = mock_server

        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
            base_url="https://custom.api.com",
            max_tokens=8192,
        )
        cli()

        mock_config_cls.assert_called_once_with(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
            base_url="https://custom.api.com",
            max_tokens=8192,
            thinking=None,
            reasoning_effort=None,
        )

    @patch("psi_agent.ai.anthropic_messages.cli.asyncio.run")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesServer")
    @patch("psi_agent.ai.anthropic_messages.cli.AnthropicMessagesConfig")
    @patch("psi_agent.ai.anthropic_messages.cli.mask_sensitive_args")
    def test_cli_call_creates_server(
        self,
        mock_mask: MagicMock,
        mock_config_cls: MagicMock,
        mock_server_cls: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI __call__ creates server with config."""
        mock_config = MagicMock()
        mock_config_cls.return_value = mock_config
        mock_server = MagicMock()
        mock_server.start = AsyncMock()
        mock_server.stop = AsyncMock()
        mock_server_cls.return_value = mock_server

        cli = AnthropicMessages(
            session_socket="/tmp/test.sock",
            model="claude-3-opus",
            api_key="test-key",
        )
        cli()

        mock_server_cls.assert_called_once_with(mock_config)


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
        """Test main calls tyro.cli."""
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
