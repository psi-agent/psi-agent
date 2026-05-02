"""CLI entry point for Telegram channel."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.channel.telegram.bot import TelegramBot
from psi_agent.channel.telegram.config import TelegramConfig


@dataclass
class Telegram:
    """Run the Telegram channel for bot conversation.

    Args:
        token: Telegram bot token.
        session_socket: Path to the Unix socket for communication with psi-session.
        proxy: Optional proxy URL for connecting to Telegram API. Supports socks5://,
            http://, and https:// formats. For SOCKS5 proxies, you must install the
            'socks' extra dependency: `pip install 'psi-agent[socks]'` or `uv sync --extra socks`.
            Defaults to None (direct connection).
        stream: Enable streaming mode (default: streaming enabled).
        stream_interval: Minimum time interval (in seconds) between message edits
            when streaming. Defaults to 1.0.
    """

    token: str
    session_socket: str
    proxy: str | None = None
    stream: bool = True
    stream_interval: float = 1.0

    def __call__(self) -> None:
        logger.info("Starting psi-channel-telegram")
        logger.debug(
            f"Config: session_socket={self.session_socket}, stream={self.stream}, "
            f"stream_interval={self.stream_interval}"
        )

        config = TelegramConfig(
            token=self.token,
            session_socket=self.session_socket,
            proxy=self.proxy,
            stream=self.stream,
            stream_interval=self.stream_interval,
        )
        bot = TelegramBot(config)

        asyncio.run(bot.start())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(Telegram)()


if __name__ == "__main__":
    main()
