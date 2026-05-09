"""Tests for pack module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import anyio
import pytest

from psi_agent.workspace.pack.api import PackError, pack


class TestPack:
    """Tests for pack function."""

    async def test_pack_creates_squashfs(self, tmp_path) -> None:
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

    async def test_pack_with_tag(self, tmp_path) -> None:
        """Pack with tag creates squashfs with tagged layer."""
        workspace = anyio.Path(tmp_path)
        input_dir = workspace / "workspace"
        await input_dir.mkdir()
        await (input_dir / "test.txt").write_text("test")

        output_file = workspace / "workspace.squashfs"

        await pack(input_dir, output_file, tag="v1.0")

        assert await output_file.exists()

    async def test_pack_nonexistent_input(self, tmp_path) -> None:
        """Pack raises error for nonexistent input directory."""
        workspace = anyio.Path(tmp_path)
        output_file = workspace / "output.squashfs"

        with pytest.raises(PackError, match="does not exist"):
            await pack(workspace / "nonexistent", output_file)

    async def test_pack_file_as_input(self, tmp_path) -> None:
        """Pack raises error when input is a file."""
        workspace = anyio.Path(tmp_path)
        input_file = workspace / "file.txt"
        await input_file.write_text("test")

        output_file = workspace / "output.squashfs"

        with pytest.raises(PackError, match="not a directory"):
            await pack(input_file, output_file)


class TestPackMksquashfsFailure:
    """Tests for pack with mksquashfs subprocess failure."""

    async def test_pack_mksquashfs_failure_raises_pack_error(self, tmp_path) -> None:
        """Pack raises PackError when mksquashfs command fails."""
        workspace = anyio.Path(tmp_path)
        input_dir = workspace / "workspace"
        await input_dir.mkdir()
        await (input_dir / "test.txt").write_text("test")

        output_file = workspace / "output.squashfs"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"mksquashfs error: failed")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(PackError, match="mksquashfs failed"):
                await pack(input_dir, output_file)


class TestPackEmptyDirectory:
    """Tests for pack with empty directory."""

    async def test_pack_empty_directory_success(self, tmp_path) -> None:
        """Pack succeeds with empty directory."""
        workspace = anyio.Path(tmp_path)
        input_dir = workspace / "workspace"
        await input_dir.mkdir()

        output_file = workspace / "output.squashfs"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            await pack(input_dir, output_file)

            # Verify mksquashfs was called
            mock_exec.assert_called_once()


class TestPackError:
    """Tests for PackError exception class."""

    def test_pack_error_message_preservation(self) -> None:
        """PackError preserves the error message."""
        error = PackError("Test error message")
        assert str(error) == "Test error message"

    def test_pack_error_inheritance(self) -> None:
        """PackError inherits from Exception."""
        error = PackError("Test")
        assert isinstance(error, Exception)

    def test_pack_error_with_mksquashfs_message(self) -> None:
        """PackError preserves mksquashfs error details."""
        error = PackError("mksquashfs failed: permission denied")
        assert "mksquashfs" in str(error)
        assert "permission denied" in str(error)
