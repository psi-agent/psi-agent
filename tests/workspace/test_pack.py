"""Tests for pack module."""

from __future__ import annotations

from pathlib import Path

import pytest

from psi_agent.workspace.pack.api import PackError, pack


class TestPack:
    """Tests for pack function."""

    async def test_pack_creates_squashfs(self, tmp_path: Path) -> None:
        """Pack creates a valid squashfs file."""
        # Create input workspace
        input_dir = tmp_path / "workspace"
        input_dir.mkdir()
        (input_dir / "tools").mkdir()
        (input_dir / "tools" / "test.py").write_text("# test tool")

        # Create output path
        output_file = tmp_path / "workspace.squashfs"

        # Pack
        await pack(input_dir, output_file)

        # Verify output exists
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    async def test_pack_with_tag(self, tmp_path: Path) -> None:
        """Pack with tag creates squashfs with tagged layer."""
        input_dir = tmp_path / "workspace"
        input_dir.mkdir()
        (input_dir / "test.txt").write_text("test")

        output_file = tmp_path / "workspace.squashfs"

        await pack(input_dir, output_file, tag="v1.0")

        assert output_file.exists()

    async def test_pack_nonexistent_input(self, tmp_path: Path) -> None:
        """Pack raises error for nonexistent input directory."""
        output_file = tmp_path / "output.squashfs"

        with pytest.raises(PackError, match="does not exist"):
            await pack(tmp_path / "nonexistent", output_file)

    async def test_pack_file_as_input(self, tmp_path: Path) -> None:
        """Pack raises error when input is a file."""
        input_file = tmp_path / "file.txt"
        input_file.write_text("test")

        output_file = tmp_path / "output.squashfs"

        with pytest.raises(PackError, match="not a directory"):
            await pack(input_file, output_file)
