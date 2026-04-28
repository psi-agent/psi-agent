"""Tests for unpack module."""

from pathlib import Path

import pytest

from psi_agent.workspace.pack.api import pack
from psi_agent.workspace.unpack.api import UnpackError, unpack


class TestUnpack:
    """Tests for unpack function."""

    async def test_unpack_creates_directory(self, tmp_path: Path) -> None:
        """Unpack creates directory with squashfs contents."""
        # Create and pack a workspace
        input_dir = tmp_path / "workspace"
        input_dir.mkdir()
        (input_dir / "tools").mkdir()
        (input_dir / "tools" / "test.py").write_text("# test tool")

        squashfs_file = tmp_path / "workspace.squashfs"
        await pack(input_dir, squashfs_file)

        # Unpack
        output_dir = tmp_path / "unpacked"
        await unpack(squashfs_file, output_dir)

        # Verify output exists
        assert output_dir.exists()
        assert (output_dir / "manifest.json").exists()

    async def test_unpack_nonexistent_input(self, tmp_path: Path) -> None:
        """Unpack raises error for nonexistent input file."""
        output_dir = tmp_path / "output"

        with pytest.raises(UnpackError, match="does not exist"):
            await unpack(tmp_path / "nonexistent.squashfs", output_dir)

    async def test_unpack_directory_as_input(self, tmp_path: Path) -> None:
        """Unpack raises error when input is a directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        output_dir = tmp_path / "output"

        with pytest.raises(UnpackError, match="not a file"):
            await unpack(input_dir, output_dir)
