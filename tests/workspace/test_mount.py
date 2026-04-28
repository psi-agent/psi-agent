"""Tests for mount module."""

from pathlib import Path
from uuid import uuid4

import pytest

from psi_agent.workspace.manifest import Layer, Manifest
from psi_agent.workspace.mount.api import MountError, _resolve_target_layer, mount


class TestResolveTargetLayer:
    """Tests for _resolve_target_layer function."""

    def test_resolve_default_layer(self) -> None:
        """Resolve default layer when no layer specified."""
        uuid1 = uuid4()
        manifest = Manifest(
            layers={uuid1: Layer(tag="v1.0")},
            default=uuid1,
        )
        result = _resolve_target_layer(manifest, None)
        assert result == uuid1

    def test_resolve_by_uuid(self) -> None:
        """Resolve layer by UUID string."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        manifest = Manifest(
            layers={
                uuid1: Layer(),
                uuid2: Layer(parent=uuid1),
            },
            default=uuid2,
        )
        result = _resolve_target_layer(manifest, str(uuid1))
        assert result == uuid1

    def test_resolve_by_tag(self) -> None:
        """Resolve layer by tag."""
        uuid1 = uuid4()
        manifest = Manifest(
            layers={uuid1: Layer(tag="v1.0")},
            default=uuid1,
        )
        result = _resolve_target_layer(manifest, "v1.0")
        assert result == uuid1

    def test_resolve_invalid_layer(self) -> None:
        """Raise error for invalid layer."""
        manifest = Manifest()
        with pytest.raises(MountError, match="not found"):
            _resolve_target_layer(manifest, "invalid")


class TestMount:
    """Tests for mount function."""

    async def test_mount_nonexistent_input(self, tmp_path: Path) -> None:
        """Mount raises error for nonexistent input file."""
        output_dir = tmp_path / "mounted"

        with pytest.raises(MountError, match="does not exist"):
            await mount(tmp_path / "nonexistent.squashfs", output_dir)

    async def test_mount_directory_as_input(self, tmp_path: Path) -> None:
        """Mount raises error when input is a directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        output_dir = tmp_path / "mounted"

        with pytest.raises(MountError, match="not a file"):
            await mount(input_dir, output_dir)
