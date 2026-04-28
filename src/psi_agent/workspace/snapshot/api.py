"""Snapshot API for creating workspace snapshots."""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

import anyio
from loguru import logger

from psi_agent.workspace.manifest import Layer, Manifest, parse_manifest, serialize_manifest


class SnapshotError(Exception):
    """Raised when snapshot operation fails."""

    pass


async def snapshot(
    input_file: str | Path,
    mount_point: str | Path,
    output_file: str | None = None,
    tag: str | None = None,
) -> None:
    """Create a snapshot of a mounted workspace.

    Args:
        input_file: Path to the original squashfs file.
        mount_point: Path to the overlayfs mount point.
        output_file: Optional path for output squashfs. Defaults to overwriting input.
        tag: Optional tag for the new layer.

    Raises:
        SnapshotError: If snapshot operation fails.
    """
    input_path = Path(await anyio.Path(input_file).resolve())
    mount_path = Path(await anyio.Path(mount_point).resolve())

    # Validate inputs
    if not await anyio.Path(input_path).exists():
        raise SnapshotError(f"Input file does not exist: {input_path}")
    if not await anyio.Path(mount_path).exists():
        raise SnapshotError(f"Mount point does not exist: {mount_path}")

    # Determine output path
    output_path = Path(await anyio.Path(output_file).resolve()) if output_file else input_path

    logger.info(f"Creating snapshot from {mount_path} to {output_path}")
    logger.debug(f"Input: {input_path}, Tag: {tag}")

    # Read mount info to get upper directory
    mount_info_path = mount_path / ".psi-mount-info"
    if not await anyio.Path(mount_info_path).exists():
        raise SnapshotError(f"Mount info file not found: {mount_info_path}")

    async with await anyio.open_file(mount_info_path) as f:
        info_content = await f.read()

    import ast

    try:
        mount_info = ast.literal_eval(info_content)
    except (SyntaxError, ValueError) as e:
        raise SnapshotError(f"Invalid mount info: {e}") from e

    upper_dir = Path(mount_info["upper_dir"])

    # Check if there are any changes
    if not any(upper_dir.iterdir()):
        logger.warning("No changes detected in upper directory")

    # Read current manifest from squashfs
    manifest = await _read_manifest_from_squashfs(input_path)

    # Generate new layer UUID
    new_layer_uuid = uuid4()

    # Create new layer
    if manifest.default is None:
        raise SnapshotError("No default layer in manifest")

    new_layer = Layer(parent=manifest.default, tag=tag)

    # Update manifest
    manifest.layers[new_layer_uuid] = new_layer
    manifest.default = new_layer_uuid

    logger.debug(f"New layer: {new_layer_uuid}, parent: {manifest.default}")

    # Create temporary directory for staging
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Copy squashfs contents to temp directory
        await _extract_squashfs(input_path, temp_path)

        # Copy upper directory as new layer
        new_layer_dir = temp_path / str(new_layer_uuid)
        await _copy_directory(Path(upper_dir), new_layer_dir)

        # Write updated manifest
        manifest_path = temp_path / "manifest.json"
        manifest_content = serialize_manifest(manifest)
        async with await anyio.open_file(manifest_path, "w") as f:
            await f.write(manifest_content)

        # Create new squashfs
        temp_squashfs = temp_path / "new.squashfs"
        await _create_squashfs(temp_path, temp_squashfs)

        # Atomic move to output path
        if await anyio.Path(output_path).exists():
            # Create temp file in same directory for atomic move
            temp_output = output_path.with_suffix(".tmp")
            shutil.move(str(temp_squashfs), str(temp_output))
            shutil.move(str(temp_output), str(output_path))
        else:
            shutil.move(str(temp_squashfs), str(output_path))

    logger.info(f"Successfully created snapshot at {output_path}")


async def _read_manifest_from_squashfs(squashfs_file: Path) -> Manifest:
    """Read manifest from squashfs file.

    Args:
        squashfs_file: Path to squashfs file.

    Returns:
        Manifest object.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract just the manifest.json
        cmd = ["unsquashfs", "-d", str(temp_path), str(squashfs_file), "manifest.json"]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

        manifest_path = temp_path / "manifest.json"
        if not await anyio.Path(manifest_path).exists():
            raise SnapshotError("manifest.json not found in squashfs")

        async with await anyio.open_file(manifest_path) as f:
            content = await f.read()

        return parse_manifest(content)


async def _extract_squashfs(squashfs_file: Path, output_dir: Path) -> None:
    """Extract squashfs contents to directory.

    Args:
        squashfs_file: Path to squashfs file.
        output_dir: Path to output directory.
    """
    cmd = ["unsquashfs", "-d", str(output_dir), str(squashfs_file)]
    logger.debug(f"Running: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "Unknown error"
        raise SnapshotError(f"Failed to extract squashfs: {error_msg}")


async def _copy_directory(src: Path, dst: Path) -> None:
    """Copy directory contents.

    Args:
        src: Source directory.
        dst: Destination directory.
    """
    await anyio.Path(dst).mkdir(parents=True, exist_ok=True)

    async for item in anyio.Path(src).iterdir():
        dest_item = dst / item.name
        if await anyio.Path(item).is_dir():
            await _copy_directory(Path(item), dest_item)
        else:
            async with await anyio.open_file(item, "rb") as src_file:
                content = await src_file.read()
            async with await anyio.open_file(dest_item, "wb") as dst_file:
                await dst_file.write(content)


async def _create_squashfs(src_dir: Path, output_file: Path) -> None:
    """Create squashfs from directory.

    Args:
        src_dir: Source directory.
        output_file: Output squashfs file.
    """
    cmd = ["mksquashfs", str(src_dir), str(output_file), "-noappend", "-comp", "xz"]
    logger.debug(f"Running: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "Unknown error"
        raise SnapshotError(f"Failed to create squashfs: {error_msg}")
