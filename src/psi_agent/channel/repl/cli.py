"""CLI entry point for REPL channel."""

import asyncio

import tyro
from loguru import logger

from psi_agent.channel.repl.config import ReplConfig
from psi_agent.channel.repl.repl import Repl


def run(session_socket: str) -> None:
    """Run the REPL channel for interactive conversation.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
    """
    logger.info("Starting psi-channel-repl")
    logger.debug(f"Config: session_socket={session_socket}")

    config = ReplConfig(session_socket=session_socket)
    repl = Repl(config)

    asyncio.run(repl.run())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
