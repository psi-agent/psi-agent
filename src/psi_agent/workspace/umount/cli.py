"""CLI entry point for psi-workspace-umount."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro

from psi_agent.workspace.umount.api import umount


@dataclass
class Umount:
    """Unmount an overlayfs workspace."""

    mount_point: str

    def __call__(self) -> None:
        asyncio.run(umount(self.mount_point))


def main() -> None:
    """CLI entry point."""
    tyro.cli(Umount)


if __name__ == "__main__":
    main()
