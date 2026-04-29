"""Tests for Anthropic Messages CLI module."""

from __future__ import annotations

from psi_agent.ai.anthropic_messages.cli import AnthropicMessages
from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig


class TestAnthropicMessagesCli:
    """Tests for Anthropic Messages CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        # Test instantiation
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
