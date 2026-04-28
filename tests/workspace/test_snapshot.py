"""Tests for snapshot module."""

from pathlib import Path

import pytest

from psi_agent.workspace.snapshot.api import SnapshotError, snapshot


class TestSnapshot:
    """Tests for snapshot function."""

    async def test_snapshot_nonexistent_input(self, tmp_path: Path) -> None:
        """Snapshot raises error for nonexistent input file."""
        mount_point = tmp_path / "mounted"
        mount_point.mkdir()

        with pytest.raises(SnapshotError, match="Input file does not exist"):
            await snapshot(tmp_path / "nonexistent.squashfs", mount_point)

    async def test_snapshot_nonexistent_mount_point(self, tmp_path: Path) -> None:
        """Snapshot raises error for nonexistent mount point."""
        input_file = tmp_path / "workspace.squashfs"
        input_file.touch()

        with pytest.raises(SnapshotError, match="Mount point does not exist"):
            await snapshot(input_file, tmp_path / "nonexistent")

    async def test_snapshot_missing_mount_info(self, tmp_path: Path) -> None:
        """Snapshot raises error when mount info is missing."""
        input_file = tmp_path / "workspace.squashfs"
        input_file.touch()

        mount_point = tmp_path / "mounted"
        mount_point.mkdir()

        with pytest.raises(SnapshotError, match="Mount info file not found"):
            await snapshot(input_file, mount_point)
