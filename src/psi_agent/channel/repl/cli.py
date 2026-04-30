"""CLI entry point for REPL channel."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.channel.repl.config import ReplConfig
from psi_agent.channel.repl.repl import Repl as ReplRunner


@dataclass
class Repl:
    """Run the REPL channel for interactive conversation."""

    session_socket: str
    stream: bool = True
    """Enable streaming mode (default: streaming enabled)."""

    def __call__(self) -> None:
        logger.info("Starting psi-channel-repl")
        logger.debug(f"Config: session_socket={self.session_socket}, stream={self.stream}")

        config = ReplConfig(session_socket=self.session_socket, stream=self.stream)
        repl = ReplRunner(config)

        asyncio.run(repl.run())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(Repl)()


if __name__ == "__main__":
    main()
