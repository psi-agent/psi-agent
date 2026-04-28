"""CLI entry point for psi-workspace-mount."""

import asyncio

import tyro

from psi_agent.workspace.mount.api import mount


def run(
    input_file: str,
    output_dir: str,
    layer: str | None = None,
) -> None:
    """Mount a squashfs image as overlayfs to a directory.

    Args:
        input_file: Path to the squashfs file.
        output_dir: Path for the mount point.
        layer: Optional layer UUID or tag to mount.
    """
    asyncio.run(mount(input_file, output_dir, layer))


def main() -> None:
    """CLI entry point."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
