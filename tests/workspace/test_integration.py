"""Integration tests for workspace components.

Note: These tests require root privileges for mount operations.
Run with: sudo uv run pytest tests/workspace/test_integration.py -v
"""

from __future__ import annotations

import os
from pathlib import Path as SyncPath

import anyio
import pytest

from psi_agent.workspace.pack.api import pack
from psi_agent.workspace.unpack.api import unpack


@pytest.mark.skipif(os.geteuid() != 0, reason="Requires root privileges")
class TestIntegration:
    """Integration tests for workspace components."""

    async def test_pack_unpack_roundtrip(self, tmp_path: SyncPath) -> None:
        """Pack and unpack should preserve workspace contents."""
        # Create input workspace
        input_dir = anyio.Path(tmp_path) / "workspace"
        await input_dir.mkdir()
        await (input_dir / "tools").mkdir()
        await (input_dir / "tools" / "test.py").write_text("# test tool")
        await (input_dir / "skills").mkdir()
        await (input_dir / "skills" / "example").mkdir()
        await (input_dir / "skills" / "example" / "SKILL.md").write_text(
            "---\nname: test\n---\nTest skill"
        )

        # Pack
        squashfs_file = anyio.Path(tmp_path) / "workspace.squashfs"
        await pack(input_dir, squashfs_file, tag="v1.0")

        # Unpack
        output_dir = anyio.Path(tmp_path) / "unpacked"
        await unpack(squashfs_file, output_dir)

        # Verify contents
        assert await (output_dir / "manifest.json").exists()
        # The layer directory name is a UUID, so we check for any directory
        layer_dirs = [
            d async for d in output_dir.iterdir() if await d.is_dir() and d.name != "manifest.json"
        ]
        assert len(layer_dirs) == 1

        layer_dir = layer_dirs[0]
        assert await (layer_dir / "tools" / "test.py").exists()
        assert await (layer_dir / "skills" / "example" / "SKILL.md").exists()


class TestNonPrivileged:
    """Tests that don't require root privileges."""

    async def test_pack_creates_valid_squashfs(self, tmp_path: SyncPath) -> None:
        """Pack creates a valid squashfs file."""
        input_dir = anyio.Path(tmp_path) / "workspace"
        await input_dir.mkdir()
        await (input_dir / "test.txt").write_text("hello")

        squashfs_file = anyio.Path(tmp_path) / "workspace.squashfs"
        await pack(input_dir, squashfs_file)

        assert await squashfs_file.exists()
        assert (await squashfs_file.stat()).st_size > 0
