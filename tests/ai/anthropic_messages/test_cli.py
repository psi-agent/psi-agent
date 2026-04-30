"""Tests for Anthropic Messages CLI module."""

from __future__ import annotations

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
