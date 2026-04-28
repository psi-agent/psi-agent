"""CLI entry point for Anthropic Messages server."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig
from psi_agent.ai.anthropic_messages.server import AnthropicMessagesServer


@dataclass
class AnthropicMessages:
    """Run Anthropic messages server."""

    session_socket: str
    model: str
    api_key: str
    base_url: str = "https://api.anthropic.com"

    def __call__(self) -> None:
        config = AnthropicMessagesConfig(
            session_socket=self.session_socket,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
        )

        logger.info("Starting psi-ai-anthropic-messages")
        logger.debug(
            f"Config: session_socket={self.session_socket}, "
            f"model={self.model}, base_url={self.base_url}"
        )

        server = AnthropicMessagesServer(config)

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
    tyro.cli(AnthropicMessages)()


if __name__ == "__main__":
    main()
