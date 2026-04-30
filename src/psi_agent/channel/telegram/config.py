"""Configuration for Telegram channel."""

from __future__ import annotations

from dataclasses import dataclass

import anyio


@dataclass
class TelegramConfig:
    """Configuration for the Telegram channel.

    Args:
        token: Telegram bot token.
        session_socket: Path to the Unix socket for communication with psi-session.
        proxy: Optional proxy URL for connecting to Telegram API. Supports socks5://,
            http://, and https:// formats. Defaults to None (direct connection).
        stream: Enable streaming mode for real-time message updates via editing.
            Defaults to True.
        stream_interval: Minimum time interval (in seconds) between message edits
            when streaming. Helps avoid Telegram API rate limits. Defaults to 1.0.
    """

    token: str
    session_socket: str
    proxy: str | None = None
    stream: bool = True
    stream_interval: float = 1.0

    def socket_path(self) -> anyio.Path:
        """Get the socket path as a Path object."""
        return anyio.Path(self.session_socket)
