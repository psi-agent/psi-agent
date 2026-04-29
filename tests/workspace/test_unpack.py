"""Tests for unpack module."""

from __future__ import annotations

import anyio
import pytest

from psi_agent.workspace.pack.api import pack
from psi_agent.workspace.unpack.api import UnpackError, unpack


class TestUnpack:
    """Tests for unpack function."""

    async def test_unpack_creates_directory(self, tmp_path) -> None:
        """Unpack creates directory with squashfs contents."""
        workspace = anyio.Path(tmp_path)
        # Create and pack a workspace
        input_dir = workspace / "workspace"
        await input_dir.mkdir()
        await (input_dir / "tools").mkdir()
        await (input_dir / "tools" / "test.py").write_text("# test tool")

        squashfs_file = workspace / "workspace.squashfs"
        await pack(input_dir, squashfs_file)

        # Unpack
        output_dir = workspace / "unpacked"
        await unpack(squashfs_file, output_dir)

        # Verify output exists
        assert await output_dir.exists()
        assert await (output_dir / "manifest.json").exists()

    async def test_unpack_nonexistent_input(self, tmp_path) -> None:
        """Unpack raises error for nonexistent input file."""
        workspace = anyio.Path(tmp_path)
        output_dir = workspace / "output"

        with pytest.raises(UnpackError, match="does not exist"):
            await unpack(workspace / "nonexistent.squashfs", output_dir)

    async def test_unpack_directory_as_input(self, tmp_path) -> None:
        """Unpack raises error when input is a directory."""
        workspace = anyio.Path(tmp_path)
        input_dir = workspace / "input"
        await input_dir.mkdir()

        output_dir = workspace / "output"

        with pytest.raises(UnpackError, match="not a file"):
            await unpack(input_dir, output_dir)
