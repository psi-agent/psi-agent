"""Tests for OpenAI completions CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.ai.openai_completions.cli import OpenaiCompletions, main
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


class TestOpenaiCompletionsCliCall:
    """Tests for OpenAI completions CLI __call__ method."""

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsServer")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsConfig")
    @patch("psi_agent.ai.openai_completions.cli.mask_sensitive_args")
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

        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
        )
        cli()

        mock_mask.assert_called_once_with(["api_key"])

    @patch("psi_agent.ai.openai_completions.cli.asyncio.run")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsServer")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsConfig")
    @patch("psi_agent.ai.openai_completions.cli.mask_sensitive_args")
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

        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
            base_url="https://custom.api.com/v1",
        )
        cli()

        mock_config_cls.assert_called_once_with(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            thinking=None,
            reasoning_effort=None,
        )

    @patch("psi_agent.ai.openai_completions.cli.asyncio.run")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsServer")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsConfig")
    @patch("psi_agent.ai.openai_completions.cli.mask_sensitive_args")
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

        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
        )
        cli()

        mock_server_cls.assert_called_once_with(mock_config)


class TestOpenaiCompletionsMain:
    """Tests for OpenAI completions CLI main function."""

    @patch("psi_agent.ai.openai_completions.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main calls tyro.cli."""
        main()
        mock_cli.assert_called_once_with(OpenaiCompletions)
