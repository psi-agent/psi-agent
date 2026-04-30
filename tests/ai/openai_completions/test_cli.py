"""Tests for OpenAI completions CLI module."""

from __future__ import annotations

import asyncio
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
        assert callable(main)

    @patch("psi_agent.ai.openai_completions.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """Test main function calls tyro.cli."""
        main()
        mock_cli.assert_called_once_with(OpenaiCompletions)

    @patch("psi_agent.ai.openai_completions.cli.mask_sensitive_args")
    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsServer")
    @patch("psi_agent.ai.openai_completions.cli.asyncio.run")
    def test_cli_call_masks_sensitive_args(
        self, mock_run: MagicMock, mock_server: MagicMock, mock_mask: MagicMock
    ) -> None:
        """Test CLI __call__ masks sensitive arguments."""
        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="secret-key",
        )
        cli()

        mock_mask.assert_called_once_with(["api_key"])

    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsServer")
    @patch("psi_agent.ai.openai_completions.cli.asyncio.run")
    def test_cli_call_creates_server(
        self, mock_run: MagicMock, mock_server_class: MagicMock
    ) -> None:
        """Test CLI __call__ creates server with correct config."""
        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
            base_url="https://custom.api.com/v1",
        )
        cli()

        mock_server_class.assert_called_once()
        call_args = mock_server_class.call_args
        config = call_args[0][0]
        assert isinstance(config, OpenAICompletionsConfig)
        assert config.session_socket == "/tmp/test.sock"
        assert config.model == "gpt-4"
        assert config.api_key == "test-key"
        assert config.base_url == "https://custom.api.com/v1"

    @patch("psi_agent.ai.openai_completions.cli.OpenAICompletionsServer")
    @patch("psi_agent.ai.openai_completions.cli.asyncio.run")
    def test_cli_call_starts_server(
        self, mock_run: MagicMock, mock_server_class: MagicMock
    ) -> None:
        """Test CLI __call__ starts server."""
        mock_server = AsyncMock()
        mock_server_class.return_value = mock_server

        cli = OpenaiCompletions(
            session_socket="/tmp/test.sock",
            model="gpt-4",
            api_key="test-key",
        )
        cli()

        # Verify asyncio.run was called
        mock_run.assert_called_once()

    def test_cli_call_runs_async_loop(self) -> None:
        """Test CLI __call__ runs the async event loop."""
        call_count = [0]

        def mock_run(coro):
            call_count[0] += 1
            # Don't actually run the coroutine

        with (
            patch.object(asyncio, "run", side_effect=mock_run),
            patch("psi_agent.ai.openai_completions.cli.mask_sensitive_args"),
            patch(
                "psi_agent.ai.openai_completions.cli.OpenAICompletionsServer"
            ) as mock_server_class,
        ):
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server

            cli = OpenaiCompletions(
                session_socket="/tmp/test.sock",
                model="gpt-4",
                api_key="test-key",
            )
            cli()

        assert call_count[0] == 1
