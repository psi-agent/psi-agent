"""Tests for umount module."""

from __future__ import annotations

from pathlib import Path as SyncPath
from unittest.mock import patch

import anyio
import pytest

from psi_agent.workspace.umount.api import UmountError, umount


class TestUmount:
    """Tests for umount function."""

    async def test_umount_nonexistent_mount_point(self, tmp_path: SyncPath) -> None:
        """Umount raises error for nonexistent mount point."""
        with pytest.raises(UmountError, match="does not exist"):
            await umount(anyio.Path(tmp_path) / "nonexistent")

    async def test_umount_missing_mount_info(self, tmp_path: SyncPath) -> None:
        """Umount raises error when mount info file is missing."""
        mount_dir = anyio.Path(tmp_path) / "mounted"
        await mount_dir.mkdir()

        with pytest.raises(UmountError, match="Mount info file not found"):
            await umount(mount_dir)

    async def test_umount_invalid_mount_info(self, tmp_path: SyncPath) -> None:
        """Umount raises error when mount info is invalid."""
        mount_dir = anyio.Path(tmp_path) / "mounted"
        await mount_dir.mkdir()

        # Create invalid mount info file
        mount_info = mount_dir / ".psi-mount-info"
        await mount_info.write_text("not valid python")

        with pytest.raises(UmountError, match="Invalid mount info"):
            await umount(mount_dir)

    async def test_umount_valid_mount_info_parse(self, tmp_path: SyncPath) -> None:
        """Umount correctly parses valid mount info."""
        mount_dir = anyio.Path(tmp_path) / "mounted"
        await mount_dir.mkdir()

        upper_dir = anyio.Path(tmp_path) / "upper"
        await upper_dir.mkdir()
        work_dir = anyio.Path(tmp_path) / "work"
        await work_dir.mkdir()
        squashfs_mount = anyio.Path(tmp_path) / "squashfs"
        await squashfs_mount.mkdir()

        # Create valid mount info file
        mount_info = mount_dir / ".psi-mount-info"
        mount_info_content = (
            f"{{'squashfs_mount': '{squashfs_mount}', "
            f"'upper_dir': '{upper_dir}', 'work_dir': '{work_dir}'}}"
        )
        await mount_info.write_text(mount_info_content)

        # Mock the _unmount and _cleanup_directory functions
        with (
            patch("psi_agent.workspace.umount.api._unmount") as mock_unmount,
            patch("psi_agent.workspace.umount.api._cleanup_directory") as mock_cleanup,
        ):
            mock_unmount.return_value = None
            mock_cleanup.return_value = None

            await umount(mount_dir)

            # Verify unmount was called for both mount points
            assert mock_unmount.call_count == 2
            # Verify cleanup was called for all directories
            assert mock_cleanup.call_count == 3


class TestUmountError:
    """Tests for UmountError exception."""

    def test_umount_error_message(self) -> None:
        """UmountError preserves message."""
        error = UmountError("Test error message")
        assert str(error) == "Test error message"

    def test_umount_error_inheritance(self) -> None:
        """UmountError inherits from Exception."""
        error = UmountError("Test")
        assert isinstance(error, Exception)
