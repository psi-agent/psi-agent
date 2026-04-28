"""Umount API for unmounting overlayfs workspace."""

from __future__ import annotations

import asyncio
from pathlib import Path

import anyio
from loguru import logger


class UmountError(Exception):
    """Raised when umount operation fails."""

    pass


async def umount(
    mount_point: str | Path,
) -> None:
    """Unmount an overlayfs workspace.

    Args:
        mount_point: Path to the mount point.

    Raises:
        UmountError: If umount operation fails.
    """
    mount_path = Path(mount_point).resolve()

    # Validate mount point
    if not mount_path.exists():
        raise UmountError(f"Mount point does not exist: {mount_path}")

    logger.info(f"Unmounting workspace at {mount_path}")

    # Read mount info
    mount_info_path = mount_path / ".psi-mount-info"
    if not mount_info_path.exists():
        raise UmountError(f"Mount info file not found: {mount_info_path}")

    async with await anyio.open_file(mount_info_path) as f:
        info_content = await f.read()

    # Parse mount info (simple dict-like string)
    # Format: {'squashfs_mount': '/tmp/...', 'upper_dir': '/tmp/...', 'work_dir': '/tmp/...'}
    import ast

    try:
        mount_info = ast.literal_eval(info_content)
    except (SyntaxError, ValueError) as e:
        raise UmountError(f"Invalid mount info: {e}") from e

    squashfs_mount = Path(mount_info["squashfs_mount"])
    upper_dir = Path(mount_info["upper_dir"])
    work_dir = Path(mount_info["work_dir"])

    # Unmount overlayfs
    await _unmount(mount_path)

    # Unmount squashfs
    await _unmount(squashfs_mount)

    # Clean up temporary directories
    await _cleanup_directory(upper_dir)
    await _cleanup_directory(work_dir)
    await _cleanup_directory(squashfs_mount)

    # Remove mount info file
    await anyio.Path(mount_info_path).unlink()

    logger.info(f"Successfully unmounted and cleaned up {mount_path}")


async def _unmount(mount_point: Path) -> None:
    """Unmount a filesystem.

    Args:
        mount_point: Path to mount point.

    Raises:
        UmountError: If unmount fails.
    """
    cmd = ["umount", str(mount_point)]
    logger.debug(f"Running: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "Unknown error"
        raise UmountError(f"Failed to unmount {mount_point}: {error_msg}")


async def _cleanup_directory(dir_path: Path) -> None:
    """Remove a directory and its contents.

    Args:
        dir_path: Path to directory to remove.
    """
    if not dir_path.exists():
        return

    try:
        # Remove directory contents
        for item in dir_path.iterdir():
            if item.is_dir():
                await _cleanup_directory(item)
            else:
                await anyio.Path(item).unlink()

        # Remove empty directory
        await anyio.Path(dir_path).rmdir()
        logger.debug(f"Cleaned up directory: {dir_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup directory {dir_path}: {e}")
