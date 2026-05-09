"""Tests for unpack module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

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


class TestUnpackCorruptFile:
    """Tests for unpack with corrupt input file."""

    async def test_unpack_corrupt_file_raises_unpack_error(self, tmp_path) -> None:
        """Unpack raises UnpackError when unsquashfs fails on corrupt file."""
        workspace = anyio.Path(tmp_path)
        corrupt_file = workspace / "corrupt.squashfs"
        await corrupt_file.write_bytes(b"not a valid squashfs file")

        output_dir = workspace / "output"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"read_fs: failed to read squashfs")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(UnpackError, match="unsquashfs failed"):
                await unpack(corrupt_file, output_dir)


class TestUnpackEmptyFile:
    """Tests for unpack with empty input file."""

    async def test_unpack_empty_file_raises_unpack_error(self, tmp_path) -> None:
        """Unpack raises UnpackError when unsquashfs fails on empty file."""
        workspace = anyio.Path(tmp_path)
        empty_file = workspace / "empty.squashfs"
        await empty_file.write_bytes(b"")

        output_dir = workspace / "output"

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Failed to read squashfs superblock")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process

            with pytest.raises(UnpackError, match="unsquashfs failed"):
                await unpack(empty_file, output_dir)


class TestUnpackExistingOutputDir:
    """Tests for unpack with existing output directory."""

    async def test_unpack_existing_output_dir_succeeds(self, tmp_path) -> None:
        """Unpack succeeds when output directory already exists."""
        workspace = anyio.Path(tmp_path)
        input_file = workspace / "test.squashfs"
        await input_file.write_bytes(b"fake squashfs")

        output_dir = workspace / "output"
        await output_dir.mkdir()
        await (output_dir / "existing.txt").write_text("existing content")

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            # Should not raise - output dir already existing is fine
            await unpack(input_file, output_dir)

            mock_exec.assert_called_once()


class TestUnpackError:
    """Tests for UnpackError exception class."""

    def test_unpack_error_message_preservation(self) -> None:
        """UnpackError preserves the error message."""
        error = UnpackError("Test error message")
        assert str(error) == "Test error message"

    def test_unpack_error_inheritance(self) -> None:
        """UnpackError inherits from Exception."""
        error = UnpackError("Test")
        assert isinstance(error, Exception)

    def test_unpack_error_with_unsquashfs_message(self) -> None:
        """UnpackError preserves unsquashfs error details."""
        error = UnpackError("unsquashfs failed: corrupt filesystem")
        assert "unsquashfs" in str(error)
        assert "corrupt filesystem" in str(error)
