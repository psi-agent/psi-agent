"""CLI entry point for psi-workspace-pack."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro

from psi_agent.workspace.pack.api import pack


@dataclass
class Pack:
    """Pack a workspace directory into a squashfs image."""

    input_dir: str
    output_file: str
    tag: str | None = None

    def __call__(self) -> None:
        asyncio.run(pack(self.input_dir, self.output_file, self.tag))


def main() -> None:
    """CLI entry point."""
    tyro.cli(Pack)()


if __name__ == "__main__":
    main()
