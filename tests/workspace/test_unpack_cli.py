"""Tests for unpack CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.workspace.unpack.cli import Unpack, main


class TestUnpackCliCall:
    """Tests for Unpack CLI __call__ method."""

    @patch("psi_agent.workspace.unpack.cli.asyncio.run")
    @patch("psi_agent.workspace.unpack.cli.unpack")
    def test_call_invokes_unpack_api(self, mock_unpack: AsyncMock, mock_run: MagicMock) -> None:
        """Unpack.__call__ calls the unpack API function."""
        cli = Unpack(input_file="/tmp/workspace.squashfs", output_dir="/tmp/workspace")
        cli()

        mock_run.assert_called_once()


class TestUnpackCliMain:
    """Tests for Unpack CLI main function."""

    @patch("psi_agent.workspace.unpack.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """main calls tyro.cli with Unpack class."""
        main()
        mock_cli.assert_called_once_with(Unpack)
