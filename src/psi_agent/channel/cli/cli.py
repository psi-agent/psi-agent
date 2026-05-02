"""CLI entry point for CLI channel."""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.channel.cli.client import CliClient
from psi_agent.channel.cli.config import CliConfig


@dataclass
class Cli:
    """Send a message to psi-session."""

    session_socket: str
    message: str
    stream: bool = True
    """Enable streaming mode (default: streaming enabled)."""

    def __call__(self) -> None:
        logger.info("Starting psi-channel-cli")
        logger.debug(f"Config: session_socket={self.session_socket}, stream={self.stream}")

        config = CliConfig(session_socket=self.session_socket, stream=self.stream)
        client = CliClient(config)

        asyncio.run(self._run(client))

    async def _run(self, client: CliClient) -> None:
        """Run the CLI client.

        Args:
            client: The CLI client.
        """
        async with client:
            if self.stream:
                result = await client.send_message(self.message, on_chunk=self._print_chunk)
                print()  # Newline after streaming
            else:
                result = await client.send_message(self.message)
                print(result)

            # Exit with appropriate code
            if result.startswith("Error:"):
                sys.exit(1)

    @staticmethod
    def _print_chunk(chunk: str) -> None:
        """Print each chunk as it arrives.

        Args:
            chunk: The content chunk.
        """
        print(chunk, end="", flush=True)


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(Cli)()


if __name__ == "__main__":
    main()
