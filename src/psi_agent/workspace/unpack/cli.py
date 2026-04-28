"""CLI entry point for psi-workspace-unpack."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro

from psi_agent.workspace.unpack.api import unpack


@dataclass
class Unpack:
    """Unpack a squashfs image to a directory."""

    input_file: str
    output_dir: str

    def __call__(self) -> None:
        asyncio.run(unpack(self.input_file, self.output_dir))


def main() -> None:
    """CLI entry point."""
    tyro.cli(Unpack)


if __name__ == "__main__":
    main()
