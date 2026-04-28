"""Tests for Anthropic Messages config."""

from pathlib import Path

from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig


class TestAnthropicMessagesConfig:
    """Tests for AnthropicMessagesConfig."""

    def test_config_creation(self) -> None:
        """Test creating config with required fields."""
        config = AnthropicMessagesConfig(
            session_socket="/tmp/test.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
        )

        assert config.session_socket == "/tmp/test.sock"
        assert config.model == "claude-sonnet-4-20250514"
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.anthropic.com"

    def test_config_with_custom_base_url(self) -> None:
        """Test creating config with custom base URL."""
        config = AnthropicMessagesConfig(
            session_socket="/tmp/test.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
            base_url="https://custom.anthropic.com",
        )

        assert config.base_url == "https://custom.anthropic.com"

    def test_socket_path(self) -> None:
        """Test socket_path returns Path object."""
        config = AnthropicMessagesConfig(
            session_socket="/tmp/test.sock",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
        )

        assert isinstance(config.socket_path(), Path)
        assert config.socket_path() == Path("/tmp/test.sock")
