"""CLI entry point for psi-workspace-snapshot."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro

from psi_agent.workspace.snapshot.api import snapshot


@dataclass
class Snapshot:
    """Create a snapshot of a mounted workspace."""

    input_file: str
    mount_point: str
    output_file: str | None = None
    tag: str | None = None

    def __call__(self) -> None:
        asyncio.run(snapshot(self.input_file, self.mount_point, self.output_file, self.tag))


def main() -> None:
    """CLI entry point."""
    tyro.cli(Snapshot)()


if __name__ == "__main__":
    main()
