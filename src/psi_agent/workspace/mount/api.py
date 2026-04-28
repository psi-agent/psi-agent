"""Mount API for mounting squashfs as overlayfs."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from uuid import UUID

import anyio
from loguru import logger

from psi_agent.workspace.manifest import Manifest, parse_manifest


class MountError(Exception):
    """Raised when mount operation fails."""

    pass


async def mount(
    input_file: str | Path,
    output_dir: str | Path,
    layer: str | None = None,
) -> None:
    """Mount a squashfs image as overlayfs to a directory.

    Args:
        input_file: Path to the squashfs file.
        output_dir: Path for the mount point.
        layer: Optional layer UUID or tag to mount. Defaults to manifest default.

    Raises:
        MountError: If mount operation fails.
    """
    input_path = Path(input_file).resolve()
    output_path = Path(output_dir).resolve()

    # Validate input file
    if not input_path.exists():
        raise MountError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise MountError(f"Input path is not a file: {input_path}")

    logger.info(f"Mounting squashfs from {input_path} to {output_path}")

    # Mount squashfs to temporary directory
    squashfs_mount = await _create_temp_dir("squashfs-")
    await _mount_squashfs(input_path, squashfs_mount)
    logger.debug(f"Mounted squashfs to {squashfs_mount}")

    # Read manifest
    manifest_path = squashfs_mount / "manifest.json"
    if not manifest_path.exists():
        raise MountError("manifest.json not found in squashfs")

    async with await anyio.open_file(manifest_path) as f:
        manifest_content = await f.read()
    manifest = parse_manifest(manifest_content)

    # Resolve target layer
    target_uuid = _resolve_target_layer(manifest, layer)
    logger.debug(f"Target layer: {target_uuid}")

    # Resolve layer chain
    chain = manifest.resolve_chain(target_uuid)
    logger.debug(f"Layer chain: {chain}")

    # Create overlayfs directories
    upper_dir = await _create_temp_dir("upper-")
    work_dir = await _create_temp_dir("work-")

    # Build lowerdir path
    lowerdirs = [str(squashfs_mount / str(uuid)) for uuid in reversed(chain)]
    lowerdir = ":".join(lowerdirs)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Mount overlayfs
    await _mount_overlayfs(output_path, lowerdir, upper_dir, work_dir)
    logger.info(f"Successfully mounted overlayfs to {output_path}")

    # Store mount info for later cleanup
    mount_info_path = output_path / ".psi-mount-info"
    mount_info = {
        "squashfs_mount": str(squashfs_mount),
        "upper_dir": str(upper_dir),
        "work_dir": str(work_dir),
    }
    async with await anyio.open_file(mount_info_path, "w") as f:
        await f.write(str(mount_info))


def _resolve_target_layer(manifest: Manifest, layer: str | None) -> UUID:
    """Resolve target layer from UUID, tag, or default.

    Args:
        manifest: The manifest to resolve from.
        layer: Optional layer UUID or tag string.

    Returns:
        The resolved layer UUID.

    Raises:
        MountError: If layer cannot be resolved.
    """
    if layer is None:
        if manifest.default is None:
            raise MountError("No default layer in manifest")
        return manifest.default

    # Try to parse as UUID
    try:
        uuid = UUID(layer)
        if uuid in manifest.layers:
            return uuid
    except ValueError:
        pass

    # Try to lookup by tag
    try:
        return manifest.lookup_by_tag(layer)
    except ValueError:
        pass

    # Layer not found
    available_tags = list(manifest.get_all_tags().keys())
    raise MountError(f"Layer '{layer}' not found. Available tags: {available_tags}")


async def _create_temp_dir(prefix: str) -> Path:
    """Create a temporary directory.

    Args:
        prefix: Prefix for the directory name.

    Returns:
        Path to the created directory.
    """
    temp_base = Path(tempfile.gettempdir())
    temp_dir = temp_base / f"{prefix}{tempfile.mkdtemp(prefix='')}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


async def _mount_squashfs(squashfs_file: Path, mount_point: Path) -> None:
    """Mount squashfs to directory.

    Args:
        squashfs_file: Path to squashfs file.
        mount_point: Path to mount point.

    Raises:
        MountError: If mount fails.
    """
    mount_point.mkdir(parents=True, exist_ok=True)

    cmd = ["mount", "-t", "squashfs", str(squashfs_file), str(mount_point), "-o", "loop"]
    logger.debug(f"Running: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "Unknown error"
        raise MountError(f"Failed to mount squashfs: {error_msg}")


async def _mount_overlayfs(
    mount_point: Path,
    lowerdir: str,
    upper_dir: Path,
    work_dir: Path,
) -> None:
    """Mount overlayfs to directory.

    Args:
        mount_point: Path to mount point.
        lowerdir: Colon-separated lower directory paths.
        upper_dir: Path to upper directory.
        work_dir: Path to work directory.

    Raises:
        MountError: If mount fails.
    """
    upper_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "mount",
        "-t",
        "overlay",
        "overlay",
        str(mount_point),
        "-o",
        f"lowerdir={lowerdir},upperdir={upper_dir},workdir={work_dir}",
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
        raise MountError(f"Failed to mount overlayfs: {error_msg}")
