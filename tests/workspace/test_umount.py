"""Tests for umount module."""

from pathlib import Path

import pytest

from psi_agent.workspace.umount.api import UmountError, umount


class TestUmount:
    """Tests for umount function."""

    async def test_umount_nonexistent_mount_point(self, tmp_path: Path) -> None:
        """Umount raises error for nonexistent mount point."""
        with pytest.raises(UmountError, match="does not exist"):
            await umount(tmp_path / "nonexistent")

    async def test_umount_missing_mount_info(self, tmp_path: Path) -> None:
        """Umount raises error when mount info file is missing."""
        mount_dir = tmp_path / "mounted"
        mount_dir.mkdir()

        with pytest.raises(UmountError, match="Mount info file not found"):
            await umount(mount_dir)
