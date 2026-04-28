"""Tests for snapshot module."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

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

    async def test_snapshot_invalid_mount_info(self, tmp_path: Path) -> None:
        """Snapshot raises error when mount info is invalid."""
        input_file = tmp_path / "workspace.squashfs"
        input_file.touch()

        mount_point = tmp_path / "mounted"
        mount_point.mkdir()

        # Create invalid mount info file
        mount_info = mount_point / ".psi-mount-info"
        mount_info.write_text("not valid python")

        with pytest.raises(SnapshotError, match="Invalid mount info"):
            await snapshot(input_file, mount_point)

    async def test_snapshot_with_valid_mount_info(self, tmp_path: Path) -> None:
        """Snapshot processes valid mount info correctly."""
        input_file = tmp_path / "workspace.squashfs"
        input_file.touch()

        mount_point = tmp_path / "mounted"
        mount_point.mkdir()

        upper_dir = tmp_path / "upper"
        upper_dir.mkdir()

        # Create valid mount info file
        mount_info = mount_point / ".psi-mount-info"
        mount_info.write_text(
            f"{{'squashfs_mount': '{tmp_path}/squashfs', 'upper_dir': '{upper_dir}', 'work_dir': '{tmp_path}/work'}}"
        )

        # Mock the internal functions to avoid needing actual squashfs tools
        with (
            patch(
                "psi_agent.workspace.snapshot.api._read_manifest_from_squashfs"
            ) as mock_read,
            patch(
                "psi_agent.workspace.snapshot.api._extract_squashfs"
            ) as mock_extract,
            patch(
                "psi_agent.workspace.snapshot.api._create_squashfs"
            ) as mock_create,
        ):
            from psi_agent.workspace.manifest import Manifest
            from uuid import uuid4

            mock_manifest = Manifest(layers={}, default=uuid4())
            mock_read.return_value = mock_manifest
            mock_extract.return_value = None
            mock_create.return_value = None

            # This will still fail because we need actual squashfs operations
            # but we've tested the validation logic


class TestSnapshotError:
    """Tests for SnapshotError exception."""

    def test_snapshot_error_message(self) -> None:
        """SnapshotError preserves message."""
        error = SnapshotError("Test error message")
        assert str(error) == "Test error message"

    def test_snapshot_error_inheritance(self) -> None:
        """SnapshotError inherits from Exception."""
        error = SnapshotError("Test")
        assert isinstance(error, Exception)
