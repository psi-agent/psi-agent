"""Tests for snapshot API module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import anyio
import pytest

from psi_agent.workspace.manifest import Layer, Manifest
from psi_agent.workspace.snapshot.api import (
    SnapshotError,
    _copy_directory,
    _create_squashfs,
    _extract_squashfs,
    _read_manifest_from_squashfs,
    snapshot,
)


class TestSnapshotValidation:
    """Tests for snapshot input validation."""

    async def test_snapshot_nonexistent_input(self, tmp_path: anyio.Path) -> None:
        """Snapshot raises error for nonexistent input file."""
        tmp = anyio.Path(tmp_path)
        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        with pytest.raises(SnapshotError, match="Input file does not exist"):
            await snapshot(tmp / "nonexistent.squashfs", mount_point)

    async def test_snapshot_nonexistent_mount_point(self, tmp_path: anyio.Path) -> None:
        """Snapshot raises error for nonexistent mount point."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.touch()

        with pytest.raises(SnapshotError, match="Mount point does not exist"):
            await snapshot(input_file, tmp / "nonexistent")

    async def test_snapshot_missing_mount_info(self, tmp_path: anyio.Path) -> None:
        """Snapshot raises error when mount info is missing."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.touch()

        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        with pytest.raises(SnapshotError, match="Mount info file not found"):
            await snapshot(input_file, mount_point)

    async def test_snapshot_invalid_mount_info(self, tmp_path: anyio.Path) -> None:
        """Snapshot raises error when mount info is invalid."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.touch()

        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        # Create invalid mount info file
        mount_info = mount_point / ".psi-mount-info"
        await mount_info.write_text("not valid python")

        with pytest.raises(SnapshotError, match="Invalid mount info"):
            await snapshot(input_file, mount_point)


class TestSnapshotWithValidMountInfo:
    """Tests for snapshot with valid mount info."""

    async def test_snapshot_with_empty_upper_dir(self, tmp_path: anyio.Path) -> None:
        """Snapshot handles empty upper directory (no changes)."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.touch()

        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        upper_dir = tmp / "upper"
        await upper_dir.mkdir()

        # Create valid mount info file
        mount_info = mount_point / ".psi-mount-info"
        mount_info_content = (
            f"{{'squashfs_mount': '{tmp}/squashfs', "
            f"'upper_dir': '{upper_dir}', 'work_dir': '{tmp}/work'}}"
        )
        await mount_info.write_text(mount_info_content)

        # Mock the internal functions including shutil.move
        with (
            patch(
                "psi_agent.workspace.snapshot.api._read_manifest_from_squashfs",
                new_callable=AsyncMock,
            ) as mock_read,
            patch(
                "psi_agent.workspace.snapshot.api._extract_squashfs",
                new_callable=AsyncMock,
            ) as mock_extract,
            patch(
                "psi_agent.workspace.snapshot.api._create_squashfs",
                new_callable=AsyncMock,
            ) as mock_create,
            patch("psi_agent.workspace.snapshot.api.shutil.move") as mock_move,
        ):
            default_uuid = uuid4()
            mock_manifest = Manifest(layers={default_uuid: Layer(tag="v1.0")}, default=default_uuid)
            mock_read.return_value = mock_manifest
            mock_extract.return_value = None
            mock_create.return_value = None
            mock_move.return_value = None

            # Should complete without error (logs warning about no changes)
            await snapshot(input_file, mount_point)

            mock_read.assert_called_once()
            mock_extract.assert_called_once()
            mock_create.assert_called_once()
            mock_move.assert_called()

    async def test_snapshot_with_tag(self, tmp_path: anyio.Path) -> None:
        """Snapshot with tag parameter updates manifest correctly."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.touch()

        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        upper_dir = tmp / "upper"
        await upper_dir.mkdir()
        # Add a file to indicate changes
        await (upper_dir / "test.txt").write_text("test")

        # Create valid mount info file
        mount_info = mount_point / ".psi-mount-info"
        mount_info_content = (
            f"{{'squashfs_mount': '{tmp}/squashfs', "
            f"'upper_dir': '{upper_dir}', 'work_dir': '{tmp}/work'}}"
        )
        await mount_info.write_text(mount_info_content)

        with (
            patch(
                "psi_agent.workspace.snapshot.api._read_manifest_from_squashfs",
                new_callable=AsyncMock,
            ) as mock_read,
            patch(
                "psi_agent.workspace.snapshot.api._extract_squashfs",
                new_callable=AsyncMock,
            ) as mock_extract,
            patch(
                "psi_agent.workspace.snapshot.api._create_squashfs",
                new_callable=AsyncMock,
            ) as mock_create,
            patch("psi_agent.workspace.snapshot.api.shutil.move") as mock_move,
        ):
            default_uuid = uuid4()
            mock_manifest = Manifest(layers={default_uuid: Layer(tag="v1.0")}, default=default_uuid)
            mock_read.return_value = mock_manifest
            mock_extract.return_value = None
            mock_create.return_value = None
            mock_move.return_value = None

            await snapshot(input_file, mount_point, tag="v2.0")

            mock_read.assert_called_once()
            mock_extract.assert_called_once()
            mock_create.assert_called_once()
            mock_move.assert_called()

    async def test_snapshot_no_default_layer(self, tmp_path: anyio.Path) -> None:
        """Snapshot raises error when manifest has no default layer."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.touch()

        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        upper_dir = tmp / "upper"
        await upper_dir.mkdir()
        await (upper_dir / "test.txt").write_text("test")

        # Create valid mount info file
        mount_info = mount_point / ".psi-mount-info"
        mount_info_content = (
            f"{{'squashfs_mount': '{tmp}/squashfs', "
            f"'upper_dir': '{upper_dir}', 'work_dir': '{tmp}/work'}}"
        )
        await mount_info.write_text(mount_info_content)

        with patch(
            "psi_agent.workspace.snapshot.api._read_manifest_from_squashfs",
            new_callable=AsyncMock,
        ) as mock_read:
            # Manifest with no default layer
            mock_manifest = Manifest(layers={}, default=None)
            mock_read.return_value = mock_manifest

            with pytest.raises(SnapshotError, match="No default layer in manifest"):
                await snapshot(input_file, mount_point)


class TestExtractSquashfs:
    """Tests for _extract_squashfs function."""

    async def test_extract_squashfs_success(self, tmp_path: anyio.Path) -> None:
        """Test successful squashfs extraction."""
        tmp = anyio.Path(tmp_path)
        squashfs_file = tmp / "test.squashfs"
        await squashfs_file.write_bytes(b"fake squashfs content")

        output_dir = tmp / "extracted"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await _extract_squashfs(squashfs_file, output_dir)

            mock_exec.assert_called_once()
            args = mock_exec.call_args[0]
            assert "unsquashfs" in args[0]

    async def test_extract_squashfs_failure(self, tmp_path: anyio.Path) -> None:
        """Test squashfs extraction failure."""
        tmp = anyio.Path(tmp_path)
        squashfs_file = tmp / "test.squashfs"
        await squashfs_file.write_bytes(b"invalid content")

        output_dir = tmp / "extracted"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Error: invalid squashfs")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(SnapshotError, match="Failed to extract squashfs"):
                await _extract_squashfs(squashfs_file, output_dir)


class TestCreateSquashfs:
    """Tests for _create_squashfs function."""

    async def test_create_squashfs_success(self, tmp_path: anyio.Path) -> None:
        """Test successful squashfs creation."""
        tmp = anyio.Path(tmp_path)
        src_dir = tmp / "source"
        await src_dir.mkdir()
        await (src_dir / "test.txt").write_text("test content")

        output_file = tmp / "output.squashfs"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await _create_squashfs(src_dir, output_file)

            mock_exec.assert_called_once()
            args = mock_exec.call_args[0]
            assert "mksquashfs" in args[0]

    async def test_create_squashfs_permission_denied(self, tmp_path: anyio.Path) -> None:
        """Test squashfs creation with permission denied."""
        tmp = anyio.Path(tmp_path)
        src_dir = tmp / "source"
        await src_dir.mkdir()

        output_file = tmp / "output.squashfs"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Permission denied")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(SnapshotError, match="Failed to create squashfs"):
                await _create_squashfs(src_dir, output_file)

    async def test_create_squashfs_disk_space_error(self, tmp_path: anyio.Path) -> None:
        """Test squashfs creation with disk space error."""
        tmp = anyio.Path(tmp_path)
        src_dir = tmp / "source"
        await src_dir.mkdir()

        output_file = tmp / "output.squashfs"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"No space left on device")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(SnapshotError, match="Failed to create squashfs"):
                await _create_squashfs(src_dir, output_file)


class TestCopyDirectory:
    """Tests for _copy_directory function."""

    async def test_copy_directory_with_files(self, tmp_path: anyio.Path) -> None:
        """Test copying directory with files."""
        tmp = anyio.Path(tmp_path)
        src_dir = tmp / "source"
        await src_dir.mkdir()
        await (src_dir / "file1.txt").write_text("content1")
        await (src_dir / "file2.txt").write_text("content2")

        dst_dir = tmp / "destination"

        await _copy_directory(src_dir, dst_dir)

        assert await (dst_dir / "file1.txt").read_text() == "content1"
        assert await (dst_dir / "file2.txt").read_text() == "content2"

    async def test_copy_directory_with_subdirectories(self, tmp_path: anyio.Path) -> None:
        """Test copying directory with subdirectories."""
        tmp = anyio.Path(tmp_path)
        src_dir = tmp / "source"
        await src_dir.mkdir()
        await (src_dir / "subdir").mkdir()
        await (src_dir / "subdir" / "nested.txt").write_text("nested content")

        dst_dir = tmp / "destination"

        await _copy_directory(src_dir, dst_dir)

        assert await (dst_dir / "subdir" / "nested.txt").read_text() == "nested content"


class TestReadManifestFromSquashfs:
    """Tests for _read_manifest_from_squashfs function."""

    async def test_read_manifest_missing_file(self, tmp_path: anyio.Path) -> None:
        """Test reading manifest when file doesn't exist in squashfs."""
        tmp = anyio.Path(tmp_path)
        squashfs_file = tmp / "test.squashfs"
        await squashfs_file.write_bytes(b"fake content")

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            with pytest.raises(SnapshotError, match="manifest.json not found"):
                await _read_manifest_from_squashfs(squashfs_file)


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
