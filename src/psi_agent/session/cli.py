"""CLI entry point for psi-session."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.session.config import SessionConfig
from psi_agent.session.server import SessionServer


@dataclass
class Session:
    """Run the psi-session server."""

    channel_socket: str
    ai_socket: str
    workspace: str
    history_file: str | None = None

    def __call__(self) -> None:
        config = SessionConfig(
            channel_socket=self.channel_socket,
            ai_socket=self.ai_socket,
            workspace=self.workspace,
            history_file=self.history_file,
        )

        logger.info("Starting psi-session")
        logger.debug(
            f"Config: channel_socket={self.channel_socket}, "
            f"ai_socket={self.ai_socket}, workspace={self.workspace}"
        )

        server = SessionServer(config)

        async def _run() -> None:
            await server.start()
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
            finally:
                await server.stop()

        asyncio.run(_run())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(Session)()


if __name__ == "__main__":
    main()
