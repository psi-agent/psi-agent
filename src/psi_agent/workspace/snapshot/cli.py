"""CLI entry point for psi-workspace-snapshot."""

import asyncio

import tyro

from psi_agent.workspace.snapshot.api import snapshot


def run(
    input_file: str,
    mount_point: str,
    output_file: str | None = None,
    tag: str | None = None,
) -> None:
    """Create a snapshot of a mounted workspace.

    Args:
        input_file: Path to the original squashfs file.
        mount_point: Path to the overlayfs mount point.
        output_file: Optional path for output squashfs.
        tag: Optional tag for the new layer.
    """
    asyncio.run(snapshot(input_file, mount_point, output_file, tag))


def main() -> None:
    """CLI entry point."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
