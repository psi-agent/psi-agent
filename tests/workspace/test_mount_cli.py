"""Tests for mount CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.workspace.mount.cli import Mount, main


class TestMountCliCall:
    """Tests for Mount CLI __call__ method."""

    @patch("psi_agent.workspace.mount.cli.asyncio.run")
    @patch("psi_agent.workspace.mount.cli.mount")
    def test_call_invokes_mount_api(self, mock_mount: AsyncMock, mock_run: MagicMock) -> None:
        """Mount.__call__ calls the mount API function."""
        cli = Mount(input_file="/tmp/workspace.squashfs", output_dir="/tmp/mounted")
        cli()

        mock_run.assert_called_once()

    @patch("psi_agent.workspace.mount.cli.asyncio.run")
    @patch("psi_agent.workspace.mount.cli.mount")
    def test_call_with_layer(self, mock_mount: AsyncMock, mock_run: MagicMock) -> None:
        """Mount.__call__ works with layer parameter."""
        cli = Mount(
            input_file="/tmp/workspace.squashfs",
            output_dir="/tmp/mounted",
            layer="v1.0",
        )
        cli()

        mock_run.assert_called_once()


class TestMountCliMain:
    """Tests for Mount CLI main function."""

    @patch("psi_agent.workspace.mount.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """main calls tyro.cli with Mount class."""
        main()
        mock_cli.assert_called_once_with(Mount)
