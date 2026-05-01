"""Tests for mount API module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import anyio
import pytest

from psi_agent.workspace.manifest import Layer, Manifest
from psi_agent.workspace.mount.api import (
    MountError,
    _create_temp_dir,
    _mount_overlayfs,
    _mount_squashfs,
    _resolve_target_layer,
    mount,
)


class TestMountValidation:
    """Tests for mount input validation."""

    async def test_mount_nonexistent_input(self, tmp_path: anyio.Path) -> None:
        """Mount raises error for nonexistent input file."""
        tmp = anyio.Path(tmp_path)
        output_dir = tmp / "output"

        with pytest.raises(MountError, match="Input file does not exist"):
            await mount(tmp / "nonexistent.squashfs", output_dir)

    async def test_mount_input_is_directory(self, tmp_path: anyio.Path) -> None:
        """Mount raises error when input is a directory."""
        tmp = anyio.Path(tmp_path)
        input_dir = tmp / "input_dir"
        await input_dir.mkdir()

        output_dir = tmp / "output"

        with pytest.raises(MountError, match="Input path is not a file"):
            await mount(input_dir, output_dir)


class TestResolveTargetLayer:
    """Tests for _resolve_target_layer function."""

    def test_resolve_default_layer(self) -> None:
        """Test resolving default layer when no layer specified."""
        default_uuid = uuid4()
        manifest = Manifest(
            layers={default_uuid: Layer(tag="v1.0")},
            default=default_uuid,
        )

        result = _resolve_target_layer(manifest, None)
        assert result == default_uuid

    def test_resolve_layer_by_uuid(self) -> None:
        """Test resolving layer by UUID string."""
        layer_uuid = uuid4()
        manifest = Manifest(
            layers={layer_uuid: Layer(tag="v1.0")},
            default=layer_uuid,
        )

        result = _resolve_target_layer(manifest, str(layer_uuid))
        assert result == layer_uuid

    def test_resolve_layer_by_tag(self) -> None:
        """Test resolving layer by tag."""
        layer_uuid = uuid4()
        manifest = Manifest(
            layers={layer_uuid: Layer(tag="v1.0")},
            default=layer_uuid,
        )

        result = _resolve_target_layer(manifest, "v1.0")
        assert result == layer_uuid

    def test_resolve_no_default_layer(self) -> None:
        """Test error when no default layer and no layer specified."""
        manifest = Manifest(layers={}, default=None)

        with pytest.raises(MountError, match="No default layer in manifest"):
            _resolve_target_layer(manifest, None)

    def test_resolve_nonexistent_layer(self) -> None:
        """Test error when layer doesn't exist."""
        layer_uuid = uuid4()
        manifest = Manifest(
            layers={layer_uuid: Layer(tag="v1.0")},
            default=layer_uuid,
        )

        with pytest.raises(MountError, match="Layer 'nonexistent' not found"):
            _resolve_target_layer(manifest, "nonexistent")


class TestMountSquashfs:
    """Tests for _mount_squashfs function."""

    async def test_mount_squashfs_success(self, tmp_path: anyio.Path) -> None:
        """Test successful squashfs mount."""
        tmp = anyio.Path(tmp_path)
        squashfs_file = tmp / "test.squashfs"
        await squashfs_file.write_bytes(b"fake squashfs content")

        mount_point = tmp / "mounted"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await _mount_squashfs(squashfs_file, mount_point)

            mock_exec.assert_called_once()
            args = mock_exec.call_args[0]
            assert "mount" in args[0]
            assert "-t" in args
            assert "squashfs" in args

    async def test_mount_squashfs_permission_denied(self, tmp_path: anyio.Path) -> None:
        """Test squashfs mount with permission denied."""
        tmp = anyio.Path(tmp_path)
        squashfs_file = tmp / "test.squashfs"
        await squashfs_file.write_bytes(b"fake content")

        mount_point = tmp / "mounted"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Permission denied")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(MountError, match="Failed to mount squashfs"):
                await _mount_squashfs(squashfs_file, mount_point)

    async def test_mount_squashfs_invalid_format(self, tmp_path: anyio.Path) -> None:
        """Test squashfs mount with invalid format."""
        tmp = anyio.Path(tmp_path)
        squashfs_file = tmp / "test.squashfs"
        await squashfs_file.write_bytes(b"invalid content")

        mount_point = tmp / "mounted"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Invalid argument")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(MountError, match="Failed to mount squashfs"):
                await _mount_squashfs(squashfs_file, mount_point)


class TestMountOverlayfs:
    """Tests for _mount_overlayfs function."""

    async def test_mount_overlayfs_success(self, tmp_path: anyio.Path) -> None:
        """Test successful overlayfs mount."""
        tmp = anyio.Path(tmp_path)
        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        lowerdir = str(tmp / "lower")
        upper_dir = tmp / "upper"
        work_dir = tmp / "work"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await _mount_overlayfs(mount_point, lowerdir, upper_dir, work_dir)

            mock_exec.assert_called_once()
            args = mock_exec.call_args[0]
            assert "mount" in args[0]
            assert "-t" in args
            assert "overlay" in args

    async def test_mount_overlayfs_permission_denied(self, tmp_path: anyio.Path) -> None:
        """Test overlayfs mount with permission denied."""
        tmp = anyio.Path(tmp_path)
        mount_point = tmp / "mounted"
        await mount_point.mkdir()

        lowerdir = str(tmp / "lower")
        upper_dir = tmp / "upper"
        work_dir = tmp / "work"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Permission denied")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(MountError, match="Failed to mount overlayfs"):
                await _mount_overlayfs(mount_point, lowerdir, upper_dir, work_dir)


class TestCreateTempDir:
    """Tests for _create_temp_dir function."""

    async def test_create_temp_dir_success(self) -> None:
        """Test successful temp directory creation."""
        temp_dir = await _create_temp_dir("test-prefix-")

        assert await temp_dir.exists()
        # The path contains the prefix in its structure
        assert "test-prefix-" in str(temp_dir)

        # Cleanup
        import shutil

        shutil.rmtree(str(temp_dir))


class TestMountIntegration:
    """Integration tests for mount function with mocked subprocess."""

    async def test_mount_missing_manifest(self, tmp_path: anyio.Path) -> None:
        """Test mount fails when manifest.json is missing."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.write_bytes(b"fake squashfs")
        output_dir = tmp / "output"

        with (
            patch("asyncio.create_subprocess_exec") as mock_exec,
            patch("psi_agent.workspace.mount.api._create_temp_dir") as mock_temp,
        ):
            # Mock temp dir creation
            temp_mount = tmp / "temp_mount"
            await temp_mount.mkdir()
            mock_temp.return_value = temp_mount

            # Mock mount subprocess
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            with pytest.raises(MountError, match="manifest.json not found"):
                await mount(input_file, output_dir)


class TestMountError:
    """Tests for MountError exception."""

    def test_mount_error_message(self) -> None:
        """MountError preserves message."""
        error = MountError("Test error message")
        assert str(error) == "Test error message"

    def test_mount_error_inheritance(self) -> None:
        """MountError inherits from Exception."""
        error = MountError("Test")
        assert isinstance(error, Exception)


class TestMountWithManifest:
    """Tests for mount function with manifest handling."""

    async def test_mount_with_valid_manifest(self, tmp_path: anyio.Path) -> None:
        """Test mount with valid manifest and layer."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.write_bytes(b"fake squashfs")
        output_dir = tmp / "output"

        # Create a fake squashfs mount with valid manifest
        from uuid import uuid4

        layer_uuid = uuid4()
        fake_mount = tmp / "fake_mount"
        await fake_mount.mkdir()
        layer_dir = fake_mount / str(layer_uuid)
        await layer_dir.mkdir()
        manifest_file = fake_mount / "manifest.json"
        await manifest_file.write_text(
            f'{{"layers": {{"{layer_uuid}": {{"tag": "v1.0"}}}}, "default": "{layer_uuid}"}}'
        )

        with (
            patch("asyncio.create_subprocess_exec") as mock_exec,
            patch("psi_agent.workspace.mount.api._create_temp_dir") as mock_temp,
        ):
            # Mock temp dir creation to return our fake mount
            mock_temp.return_value = fake_mount

            # Mock mount subprocess
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await mount(input_file, output_dir)

            # Output directory should be created
            assert await output_dir.exists()

    async def test_mount_output_dir_created(self, tmp_path: anyio.Path) -> None:
        """Test mount creates output directory if it doesn't exist."""
        tmp = anyio.Path(tmp_path)
        input_file = tmp / "workspace.squashfs"
        await input_file.write_bytes(b"fake squashfs")
        output_dir = tmp / "output"

        # Create a fake squashfs mount with valid manifest
        from uuid import uuid4

        layer_uuid = uuid4()
        fake_mount = tmp / "fake_mount"
        await fake_mount.mkdir()
        layer_dir = fake_mount / str(layer_uuid)
        await layer_dir.mkdir()
        manifest_file = fake_mount / "manifest.json"
        await manifest_file.write_text(
            f'{{"layers": {{"{layer_uuid}": {{"tag": "v1.0"}}}}, "default": "{layer_uuid}"}}'
        )

        with (
            patch("asyncio.create_subprocess_exec") as mock_exec,
            patch("psi_agent.workspace.mount.api._create_temp_dir") as mock_temp,
        ):
            mock_temp.return_value = fake_mount

            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await mount(input_file, output_dir)

            # Output directory should be created
            assert await output_dir.exists()
