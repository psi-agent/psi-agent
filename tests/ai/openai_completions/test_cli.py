"""Tests for OpenAI completions CLI module."""

from __future__ import annotations

from psi_agent.ai.openai_completions.cli import OpenaiCompletions
from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig


class TestOpenaiCompletionsCli:
    """Tests for OpenAI completions CLI dataclass."""

    def test_cli_import(self) -> None:
        """Test CLI class can be imported."""
        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
        )
        assert cli.session_socket == "/tmp/test.sock"
        assert cli.model == "gpt-4"
        assert cli.api_key == "test-key"
        assert cli.base_url == "https://api.openai.com/v1"  # default

    def test_cli_with_custom_base_url(self) -> None:
        """Test CLI with custom base URL."""
        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
            base_url="https://custom.api.com/v1",
        )
        assert cli.base_url == "https://custom.api.com/v1"

    def test_cli_config_creation(self) -> None:
        """Test CLI creates valid config."""
        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
        )

        # Verify config can be created from CLI args
        config = OpenAICompletionsConfig(
            session_socket=cli.session_socket,
            model=cli.model,
            api_key=cli.api_key,
            base_url=cli.base_url,
        )
        assert config.session_socket == "/tmp/test.sock"
        assert config.model == "gpt-4"
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.openai.com/v1"

    def test_cli_with_openrouter_base_url(self) -> None:
        """Test CLI with OpenRouter base URL."""
        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="anthropic/claude-3-opus",
            api_key="sk-or-test",
            base_url="https://openrouter.ai/api/v1",
        )
        assert cli.base_url == "https://openrouter.ai/api/v1"
        assert cli.model == "anthropic/claude-3-opus"

    def test_main_exists(self) -> None:
        """Test main function exists."""
        from psi_agent.ai.openai_completions.cli import main

        assert callable(main)
