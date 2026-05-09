"""Tests for umount CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.workspace.umount.cli import Umount, main


class TestUmountCliCall:
    """Tests for Umount CLI __call__ method."""

    @patch("psi_agent.workspace.umount.cli.asyncio.run")
    @patch("psi_agent.workspace.umount.cli.umount")
    def test_call_invokes_umount_api(self, mock_umount: AsyncMock, mock_run: MagicMock) -> None:
        """Umount.__call__ calls the umount API function."""
        cli = Umount(mount_point="/tmp/mounted")
        cli()

        mock_run.assert_called_once()


class TestUmountCliMain:
    """Tests for Umount CLI main function."""

    @patch("psi_agent.workspace.umount.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """main calls tyro.cli with Umount class."""
        main()
        mock_cli.assert_called_once_with(Umount)
