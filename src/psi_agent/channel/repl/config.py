"""Configuration for REPL channel."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReplConfig:
    """Configuration for the REPL channel.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
    """

    session_socket: str

    def socket_path(self) -> Path:
        """Get the socket path as a Path object."""
        return Path(self.session_socket)
