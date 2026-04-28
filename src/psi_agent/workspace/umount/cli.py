"""CLI entry point for psi-workspace-umount."""

import asyncio

import tyro

from psi_agent.workspace.umount.api import umount


def run(
    mount_point: str,
) -> None:
    """Unmount an overlayfs workspace.

    Args:
        mount_point: Path to the mount point.
    """
    asyncio.run(umount(mount_point))


def main() -> None:
    """CLI entry point."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
