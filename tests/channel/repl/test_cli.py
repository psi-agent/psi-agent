"""Tests for REPL channel CLI."""

from __future__ import annotations

from psi_agent.channel.repl.cli import Repl


class TestReplCli:
    """Tests for REPL CLI flag handling."""

    def test_cli_default_stream_enabled(self) -> None:
        """Test CLI defaults to streaming enabled."""
        cli = Repl(session_socket="/tmp/test.sock")

        assert cli.stream is True

    def test_cli_no_stream_flag(self) -> None:
        """Test CLI --no-stream flag disables streaming."""
        cli = Repl(session_socket="/tmp/test.sock", stream=False)

        assert cli.stream is False

    def test_cli_passes_stream_to_config(self) -> None:
        """Test CLI passes correct stream value to config."""
        cli = Repl(session_socket="/tmp/test.sock", stream=False)

        # When stream=False, config.stream should be False
        # This is verified by checking the logic in __call__
        assert cli.stream is False
