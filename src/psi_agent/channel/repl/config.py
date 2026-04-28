"""Configuration for REPL channel."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ReplConfig:
    """Configuration for the REPL channel.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        history_file: Optional path to the history file. If None, uses default path.
    """

    session_socket: str
    history_file: str | None = None

    def socket_path(self) -> Path:
        """Get the socket path as a Path object."""
        return Path(self.session_socket)

    def get_history_path(self) -> Path:
        """Get the history file path.

        Returns the configured history file path or the default path
        at ~/.cache/psi-agent/repl_history.txt.
        """
        if self.history_file is not None:
            return Path(self.history_file)
        return Path.home() / ".cache" / "psi-agent" / "repl_history.txt"
