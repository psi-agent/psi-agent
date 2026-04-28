"""CLI entry point for psi-workspace-mount."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro

from psi_agent.workspace.mount.api import mount


@dataclass
class Mount:
    """Mount a squashfs image as overlayfs to a directory."""

    input_file: str
    output_dir: str
    layer: str | None = None

    def __call__(self) -> None:
        asyncio.run(mount(self.input_file, self.output_dir, self.layer))


def main() -> None:
    """CLI entry point."""
    tyro.cli(Mount)()


if __name__ == "__main__":
    main()
