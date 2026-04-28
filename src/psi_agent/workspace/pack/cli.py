"""CLI entry point for psi-workspace-pack."""

import asyncio

import tyro

from psi_agent.workspace.pack.api import pack


def run(
    input_dir: str,
    output_file: str,
    tag: str | None = None,
) -> None:
    """Pack a workspace directory into a squashfs image.

    Args:
        input_dir: Path to the workspace directory.
        output_file: Path for the output squashfs file.
        tag: Optional tag for the layer.
    """
    asyncio.run(pack(input_dir, output_file, tag))


def main() -> None:
    """CLI entry point."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
