"""Configuration for REPL channel."""

from __future__ import annotations

from dataclasses import dataclass

import anyio
from platformdirs import user_cache_dir


@dataclass
class ReplConfig:
    """Configuration for the REPL channel.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        history_file: Optional path to the history file. If None, uses default path.
    """

    session_socket: str
    history_file: str | None = None

    def socket_path(self) -> anyio.Path:
        """Get the socket path as a Path object."""
        return anyio.Path(self.session_socket)

    def get_history_path(self) -> anyio.Path:
        """Get the history file path.

        Returns the configured history file path or the default path
        at the platform-specific cache directory.
        """
        if self.history_file is not None:
            return anyio.Path(self.history_file)
        # Use platformdirs for cross-platform cache directory
        cache_dir = user_cache_dir("psi-agent")
        return anyio.Path(cache_dir) / "repl_history.txt"
