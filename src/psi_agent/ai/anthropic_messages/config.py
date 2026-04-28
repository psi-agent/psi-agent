"""Configuration for Anthropic Messages server."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnthropicMessagesConfig:
    """Configuration for the Anthropic Messages server.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        model: The model name to use for messages (e.g., "claude-sonnet-4-20250514").
        api_key: The API key for authentication.
        base_url: The base URL for the Anthropic API.
    """

    session_socket: str
    model: str
    api_key: str
    base_url: str = "https://api.anthropic.com"

    def socket_path(self) -> Path:
        """Get the socket path as a Path object."""
        return Path(self.session_socket)
