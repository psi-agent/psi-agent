"""Pack API for creating squashfs from workspace directory."""

import asyncio
import tempfile
from pathlib import Path
from uuid import uuid4

import anyio
from loguru import logger

from psi_agent.workspace.manifest import Layer, Manifest, serialize_manifest


class PackError(Exception):
    """Raised when pack operation fails."""

    pass


async def pack(
    input_dir: str | Path,
    output_file: str | Path,
    tag: str | None = None,
) -> None:
    """Pack a workspace directory into a squashfs image.

    Args:
        input_dir: Path to the workspace directory.
        output_file: Path for the output squashfs file.
        tag: Optional tag for the layer.

    Raises:
        PackError: If pack operation fails.
    """
    input_path = Path(input_dir).resolve()
    output_path = Path(output_file).resolve()

    # Validate input directory
    if not input_path.exists():
        raise PackError(f"Input directory does not exist: {input_path}")
    if not input_path.is_dir():
        raise PackError(f"Input path is not a directory: {input_path}")

    # Generate UUID for the layer
    layer_uuid = uuid4()
    layer_name = str(layer_uuid)

    logger.info(f"Packing workspace from {input_path} to {output_path}")
    logger.debug(f"Layer UUID: {layer_uuid}, Tag: {tag}")

    # Create manifest
    manifest = Manifest(
        layers={layer_uuid: Layer(tag=tag)},
        default=layer_uuid,
    )

    # Create temporary directory for staging
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create layer directory
        layer_dir = temp_path / layer_name
        layer_dir.mkdir()

        # Copy input directory contents to layer directory
        await _copy_directory(input_path, layer_dir)

        # Write manifest.json
        manifest_path = temp_path / "manifest.json"
        manifest_content = serialize_manifest(manifest)
        async with await anyio.open_file(manifest_path, "w") as f:
            await f.write(manifest_content)

        # Create squashfs
        await _create_squashfs(temp_path, output_path)

    logger.info(f"Successfully created squashfs at {output_path}")


async def _copy_directory(src: Path, dst: Path) -> None:
    """Copy directory contents asynchronously.

    Args:
        src: Source directory path.
        dst: Destination directory path.
    """
    for item in src.iterdir():
        dest_item = dst / item.name
        if item.is_dir():
            dest_item.mkdir()
            await _copy_directory(item, dest_item)
        else:
            async with await anyio.open_file(item, "rb") as src_file:
                content = await src_file.read()
            async with await anyio.open_file(dest_item, "wb") as dst_file:
                await dst_file.write(content)


async def _create_squashfs(src_dir: Path, output_file: Path) -> None:
    """Create squashfs image from directory.

    Args:
        src_dir: Source directory path.
        output_file: Output squashfs file path.

    Raises:
        PackError: If mksquashfs command fails.
    """
    # Ensure parent directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Run mksquashfs command
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
        raise PackError(f"mksquashfs failed: {error_msg}")
