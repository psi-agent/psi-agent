"""CLI entry point for Anthropic Messages server."""

import asyncio

import tyro
from loguru import logger

from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig
from psi_agent.ai.anthropic_messages.server import AnthropicMessagesServer


def run(
    session_socket: str,
    model: str,
    api_key: str,
    base_url: str = "https://api.anthropic.com",
) -> None:
    """Run the Anthropic Messages server.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        model: The model name to use for messages (e.g., "claude-sonnet-4-20250514").
        api_key: The API key for authentication.
        base_url: The base URL for the Anthropic API.
    """
    config = AnthropicMessagesConfig(
        session_socket=session_socket,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )

    logger.info("Starting psi-ai-anthropic-messages")
    logger.debug(f"Config: session_socket={session_socket}, model={model}, base_url={base_url}")

    server = AnthropicMessagesServer(config)

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
