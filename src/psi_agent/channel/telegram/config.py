"""Configuration for Telegram channel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TelegramConfig:
    """Configuration for the Telegram channel.

    Args:
        token: Telegram bot token.
        session_socket: Path to the Unix socket for communication with psi-session.
    """

    token: str
    session_socket: str

    def socket_path(self) -> Path:
        """Get the socket path as a Path object."""
        return Path(self.session_socket)
