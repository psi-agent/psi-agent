"""Unpack API for extracting squashfs to directory."""

from __future__ import annotations

import asyncio

import anyio
from loguru import logger


class UnpackError(Exception):
    """Raised when unpack operation fails."""

    pass


async def unpack(
    input_file: str | anyio.Path,
    output_dir: str | anyio.Path,
) -> None:
    """Unpack a squashfs image to a directory.

    Args:
        input_file: Path to the squashfs file.
        output_dir: Path for the output directory.

    Raises:
        UnpackError: If unpack operation fails.
    """
    input_path = anyio.Path(await anyio.Path(input_file).resolve())
    output_path = anyio.Path(await anyio.Path(output_dir).resolve())

    # Validate input file
    if not await input_path.exists():
        raise UnpackError(f"Input file does not exist: {input_path}")
    if not await input_path.is_file():
        raise UnpackError(f"Input path is not a file: {input_path}")

    logger.info(f"Unpacking squashfs from {input_path} to {output_path}")

    # Create output directory
    await output_path.mkdir(parents=True, exist_ok=True)

    # Run unsquashfs command
    cmd = [
        "unsquashfs",
        "-d",
        str(output_path),
        str(input_path),
    ]
    logger.debug(f"Running: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "Unknown error"
        raise UnpackError(f"unsquashfs failed: {error_msg}")

    logger.debug(f"unsquashfs output: {stderr.decode() if stderr else 'No output'}")

    logger.info(f"Successfully unpacked to {output_path}")
