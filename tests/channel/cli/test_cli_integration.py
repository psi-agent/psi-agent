"""Tests for CLI entry point integration."""

from __future__ import annotations

import sys
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from psi_agent.channel.cli.cli import Cli
from psi_agent.channel.cli.client import CliClient
from psi_agent.channel.cli.config import CliConfig


class TestCliCall:
    """Tests for CLI __call__ method."""

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("psi_agent.channel.cli.cli.CliClient")
    @patch("psi_agent.channel.cli.cli.CliConfig")
    def test_cli_call_creates_config_and_client(
        self, mock_config: MagicMock, mock_client: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test __call__ creates config and client."""
        mock_config.return_value = MagicMock()
        mock_client.return_value = MagicMock()

        cli = Cli(session_socket="/tmp/test.sock", message="Hello")
        cli()

        mock_config.assert_called_once_with(session_socket="/tmp/test.sock", stream=True)
        mock_client.assert_called_once()
        mock_run.assert_called_once()

    @patch("psi_agent.channel.cli.cli.asyncio.run")
    @patch("psi_agent.channel.cli.cli.CliClient")
    @patch("psi_agent.channel.cli.cli.CliConfig")
    def test_cli_call_with_stream_false(
        self, mock_config: MagicMock, mock_client: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test __call__ with stream=False."""
        mock_config.return_value = MagicMock()
        mock_client.return_value = MagicMock()

        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=False)
        cli()

        mock_config.assert_called_once_with(session_socket="/tmp/test.sock", stream=False)


class TestCliRun:
    """Tests for CLI _run method."""

    @pytest.mark.asyncio
    async def test_run_streaming_success(self) -> None:
        """Test _run with streaming mode."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=True)
        client = CliClient(config)

        # Mock the client's send_message to return success
        mock_send = AsyncMock(return_value="Test response")
        client.send_message = mock_send  # type: ignore

        # Mock the context manager
        client.__aenter__ = AsyncMock(return_value=client)  # type: ignore
        client.__aexit__ = AsyncMock(return_value=None)  # type: ignore

        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=True)

        # Capture stdout
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            await cli._run(client)
        finally:
            sys.stdout = old_stdout

        mock_send.assert_called_once()
        # Should have called with on_chunk callback

    @pytest.mark.asyncio
    async def test_run_non_streaming_success(self) -> None:
        """Test _run with non-streaming mode."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        # Mock the client's send_message to return success
        mock_send = AsyncMock(return_value="Test response")
        client.send_message = mock_send  # type: ignore

        # Mock the context manager
        client.__aenter__ = AsyncMock(return_value=client)  # type: ignore
        client.__aexit__ = AsyncMock(return_value=None)  # type: ignore

        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=False)

        # Capture stdout
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            await cli._run(client)
        finally:
            sys.stdout = old_stdout

        mock_send.assert_called_once_with("Hello")
        assert "Test response" in captured.getvalue()

    @pytest.mark.asyncio
    async def test_run_exits_on_error(self) -> None:
        """Test _run exits with code 1 on error."""
        config = CliConfig(session_socket="/tmp/test.sock", stream=False)
        client = CliClient(config)

        # Mock the client's send_message to return error
        mock_send = AsyncMock(return_value="Error: Connection failed")
        client.send_message = mock_send  # type: ignore

        # Mock the context manager
        client.__aenter__ = AsyncMock(return_value=client)  # type: ignore
        client.__aexit__ = AsyncMock(return_value=None)  # type: ignore

        cli = Cli(session_socket="/tmp/test.sock", message="Hello", stream=False)

        with pytest.raises(SystemExit) as exc_info:
            await cli._run(client)

        assert exc_info.value.code == 1


class TestMainFunction:
    """Tests for main function."""

    @patch("psi_agent.channel.cli.cli.tyro.cli")
    def test_main_calls_tyro_cli(self, mock_cli: MagicMock) -> None:
        """Test main calls tyro.cli."""
        from psi_agent.channel.cli.cli import main

        main()

        mock_cli.assert_called_once()
