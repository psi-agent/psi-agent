"""CLI entry point for Telegram channel."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.channel.telegram.bot import TelegramBot
from psi_agent.channel.telegram.config import TelegramConfig
from psi_agent.utils.proctitle import mask_sensitive_args


@dataclass
class Telegram:
    """Run the Telegram channel for bot conversation."""

    token: str
    session_socket: str

    def __call__(self) -> None:
        # Mask sensitive arguments from process title
        mask_sensitive_args(["token"])

        logger.info("Starting psi-channel-telegram")
        logger.debug(f"Config: session_socket={self.session_socket}")

        config = TelegramConfig(token=self.token, session_socket=self.session_socket)
        bot = TelegramBot(config)

        asyncio.run(bot.start())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(Telegram)()


if __name__ == "__main__":
    main()
