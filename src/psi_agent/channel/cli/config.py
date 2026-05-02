"""Configuration for CLI channel."""

from __future__ import annotations

from dataclasses import dataclass

import anyio


@dataclass
class CliConfig:
    """Configuration for the CLI channel.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        stream: Whether to use streaming mode. Default is True.
    """

    session_socket: str
    stream: bool = True

    def socket_path(self) -> anyio.Path:
        """Get the socket path as a Path object."""
        return anyio.Path(self.session_socket)
