"""Tests for pack CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.workspace.pack.cli import Pack, main


class TestPackCliCall:
    """Tests for Pack CLI __call__ method."""

    @patch("psi_agent.workspace.pack.cli.asyncio.run")
    @patch("psi_agent.workspace.pack.cli.pack")
    def test_call_invokes_pack_api(self, mock_pack: AsyncMock, mock_run: MagicMock) -> None:
        """Pack.__call__ calls the pack API function."""
        cli = Pack(input_dir="/tmp/workspace", output_file="/tmp/output.squashfs", tag="v1.0")
        cli()

        mock_run.assert_called_once()

    @patch("psi_agent.workspace.pack.cli.asyncio.run")
    @patch("psi_agent.workspace.pack.cli.pack")
    def test_call_with_no_tag(self, mock_pack: AsyncMock, mock_run: MagicMock) -> None:
        """Pack.__call__ works with no tag."""
        cli = Pack(input_dir="/tmp/workspace", output_file="/tmp/output.squashfs")
        cli()

        mock_run.assert_called_once()


class TestPackCliMain:
    """Tests for Pack CLI main function."""

    @patch("psi_agent.workspace.pack.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """main calls tyro.cli with Pack class."""
        main()
        mock_cli.assert_called_once_with(Pack)
