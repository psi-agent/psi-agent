"""Tests for umount module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import anyio
import pytest

from psi_agent.workspace.umount.api import UmountError, umount


class TestUmount:
    """Tests for umount function."""

    async def test_umount_nonexistent_mount_point(self, tmp_path) -> None:
        """Umount raises error for nonexistent mount point."""
        with pytest.raises(UmountError, match="does not exist"):
            await umount(anyio.Path(tmp_path) / "nonexistent")

    async def test_umount_missing_mount_info(self, tmp_path) -> None:
        """Umount raises error when mount info file is missing."""
        mount_dir = anyio.Path(tmp_path) / "mounted"
        await mount_dir.mkdir()

        with pytest.raises(UmountError, match="Mount info file not found"):
            await umount(mount_dir)

    async def test_umount_invalid_mount_info(self, tmp_path) -> None:
        """Umount raises error when mount info is invalid."""
        mount_dir = anyio.Path(tmp_path) / "mounted"
        await mount_dir.mkdir()

        # Create invalid mount info file
        mount_info = mount_dir / ".psi-mount-info"
        await mount_info.write_text("not valid python")

        with pytest.raises(UmountError, match="Invalid mount info"):
            await umount(mount_dir)

    async def test_umount_valid_mount_info_parse(self, tmp_path) -> None:
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


class TestUmountHelperFunctions:
    """Tests for umount helper functions."""

    async def test_unmount_failure(self, tmp_path) -> None:
        """_unmount raises UmountError when umount command fails."""
        from psi_agent.workspace.umount.api import _unmount as unmount_func

        mount_point = anyio.Path(tmp_path) / "mount"
        await mount_point.mkdir()

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Device or resource busy")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(UmountError, match="Failed to unmount"):
                await unmount_func(mount_point)

    async def test_unmount_success(self, tmp_path) -> None:
        """_unmount succeeds when umount command succeeds."""
        from psi_agent.workspace.umount.api import _unmount as unmount_func

        mount_point = anyio.Path(tmp_path) / "mount"
        await mount_point.mkdir()

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            # Should not raise
            await unmount_func(mount_point)

    async def test_cleanup_directory_nonexistent(self, tmp_path) -> None:
        """_cleanup_directory handles nonexistent directory."""
        from psi_agent.workspace.umount.api import _cleanup_directory

        nonexistent = anyio.Path(tmp_path) / "nonexistent"
        # Should not raise
        await _cleanup_directory(nonexistent)

    async def test_cleanup_directory_with_files(self, tmp_path) -> None:
        """_cleanup_directory removes directory with files."""
        from psi_agent.workspace.umount.api import _cleanup_directory

        test_dir = anyio.Path(tmp_path) / "test_dir"
        await test_dir.mkdir()
        test_file = test_dir / "test.txt"
        await test_file.write_text("test content")

        await _cleanup_directory(test_dir)

        assert not await test_dir.exists()

    async def test_cleanup_directory_with_nested_dirs(self, tmp_path) -> None:
        """_cleanup_directory removes nested directories."""
        from psi_agent.workspace.umount.api import _cleanup_directory

        test_dir = anyio.Path(tmp_path) / "test_dir"
        nested_dir = test_dir / "nested"
        await nested_dir.mkdir(parents=True)
        nested_file = nested_dir / "file.txt"
        await nested_file.write_text("nested content")

        await _cleanup_directory(test_dir)

        assert not await test_dir.exists()

    async def test_cleanup_directory_handles_error(self, tmp_path) -> None:
        """_cleanup_directory handles errors gracefully."""
        from psi_agent.workspace.umount.api import _cleanup_directory

        test_dir = anyio.Path(tmp_path) / "test_dir"
        await test_dir.mkdir()

        # Mock iterdir to raise an error
        with patch.object(anyio.Path, "iterdir", side_effect=PermissionError("denied")):
            # Should not raise, just log warning
            await _cleanup_directory(test_dir)
