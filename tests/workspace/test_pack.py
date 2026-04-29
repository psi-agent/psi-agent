"""Tests for pack module."""

from __future__ import annotations

from pathlib import Path as SyncPath

import anyio
import pytest

from psi_agent.workspace.pack.api import PackError, pack


class TestPack:
    """Tests for pack function."""

    async def test_pack_creates_squashfs(self, tmp_path: SyncPath) -> None:
        """Pack creates a valid squashfs file."""
        # Convert to anyio.Path
        workspace = anyio.Path(tmp_path)
        # Create input workspace
        input_dir = workspace / "workspace"
        await input_dir.mkdir()
        await (input_dir / "tools").mkdir()
        await (input_dir / "tools" / "test.py").write_text("# test tool")

        # Create output path
        output_file = workspace / "workspace.squashfs"

        # Pack
        await pack(input_dir, output_file)

        # Verify output exists
        assert await output_file.exists()
        assert (await output_file.stat()).st_size > 0

    async def test_pack_with_tag(self, tmp_path: SyncPath) -> None:
        """Pack with tag creates squashfs with tagged layer."""
        workspace = anyio.Path(tmp_path)
        input_dir = workspace / "workspace"
        await input_dir.mkdir()
        await (input_dir / "test.txt").write_text("test")

        output_file = workspace / "workspace.squashfs"

        await pack(input_dir, output_file, tag="v1.0")

        assert await output_file.exists()

    async def test_pack_nonexistent_input(self, tmp_path: SyncPath) -> None:
        """Pack raises error for nonexistent input directory."""
        workspace = anyio.Path(tmp_path)
        output_file = workspace / "output.squashfs"

        with pytest.raises(PackError, match="does not exist"):
            await pack(workspace / "nonexistent", output_file)

    async def test_pack_file_as_input(self, tmp_path: SyncPath) -> None:
        """Pack raises error when input is a file."""
        workspace = anyio.Path(tmp_path)
        input_file = workspace / "file.txt"
        await input_file.write_text("test")

        output_file = workspace / "output.squashfs"

        with pytest.raises(PackError, match="not a directory"):
            await pack(input_file, output_file)
