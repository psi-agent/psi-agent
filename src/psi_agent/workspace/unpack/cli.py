"""CLI entry point for psi-workspace-unpack."""

import asyncio

import tyro

from psi_agent.workspace.unpack.api import unpack


def run(
    input_file: str,
    output_dir: str,
) -> None:
    """Unpack a squashfs image to a directory.

    Args:
        input_file: Path to the squashfs file.
        output_dir: Path for the output directory.
    """
    asyncio.run(unpack(input_file, output_dir))


def main() -> None:
    """CLI entry point."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
