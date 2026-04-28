"""CLI entry point for psi-session."""

import asyncio

import tyro
from loguru import logger

from psi_agent.session.config import SessionConfig
from psi_agent.session.server import SessionServer


def run(
    channel_socket: str,
    ai_socket: str,
    workspace: str,
    history_file: str | None = None,
) -> None:
    """Run the psi-session server.

    Args:
        channel_socket: Path to the Unix socket for communication with channel.
        ai_socket: Path to the Unix socket for communication with psi-ai.
        workspace: Path to the workspace directory.
        history_file: Optional path to JSON file for history persistence.
    """
    config = SessionConfig(
        channel_socket=channel_socket,
        ai_socket=ai_socket,
        workspace=workspace,
        history_file=history_file,
    )

    logger.info("Starting psi-session")
    logger.debug(
        f"Config: channel_socket={channel_socket}, ai_socket={ai_socket}, workspace={workspace}"
    )

    server = SessionServer(config)

    async def _run() -> None:
        await server.start()
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await server.stop()

    asyncio.run(_run())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
