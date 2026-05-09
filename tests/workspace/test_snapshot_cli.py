"""Tests for snapshot CLI module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from psi_agent.workspace.snapshot.cli import Snapshot, main


class TestSnapshotCliCall:
    """Tests for Snapshot CLI __call__ method."""

    @patch("psi_agent.workspace.snapshot.cli.asyncio.run")
    @patch("psi_agent.workspace.snapshot.cli.snapshot")
    def test_call_invokes_snapshot_api(self, mock_snapshot: AsyncMock, mock_run: MagicMock) -> None:
        """Snapshot.__call__ calls the snapshot API function."""
        cli = Snapshot(
            input_file="/tmp/workspace.squashfs",
            mount_point="/tmp/mounted",
            tag="v1.1",
        )
        cli()

        mock_run.assert_called_once()

    @patch("psi_agent.workspace.snapshot.cli.asyncio.run")
    @patch("psi_agent.workspace.snapshot.cli.snapshot")
    def test_call_with_output_file(self, mock_snapshot: AsyncMock, mock_run: MagicMock) -> None:
        """Snapshot.__call__ works with output_file parameter."""
        cli = Snapshot(
            input_file="/tmp/workspace.squashfs",
            mount_point="/tmp/mounted",
            tag="v1.1",
            output_file="/tmp/workspace_v2.squashfs",
        )
        cli()

        mock_run.assert_called_once()

    @patch("psi_agent.workspace.snapshot.cli.asyncio.run")
    @patch("psi_agent.workspace.snapshot.cli.snapshot")
    def test_call_with_no_tag(self, mock_snapshot: AsyncMock, mock_run: MagicMock) -> None:
        """Snapshot.__call__ works without tag."""
        cli = Snapshot(
            input_file="/tmp/workspace.squashfs",
            mount_point="/tmp/mounted",
        )
        cli()

        mock_run.assert_called_once()


class TestSnapshotCliMain:
    """Tests for Snapshot CLI main function."""

    @patch("psi_agent.workspace.snapshot.cli.tyro.cli")
    def test_main_calls_tyro(self, mock_cli: MagicMock) -> None:
        """main calls tyro.cli with Snapshot class."""
        main()
        mock_cli.assert_called_once_with(Snapshot)
