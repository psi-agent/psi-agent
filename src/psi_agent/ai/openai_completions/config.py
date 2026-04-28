"""Configuration for OpenAI completions server."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OpenAICompletionsConfig:
    """Configuration for the OpenAI completions server.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        model: The model name to use for completions.
        api_key: The API key for authentication.
        base_url: The base URL for the OpenAI-compatible API.
    """

    session_socket: str
    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"

    def socket_path(self) -> Path:
        """Get the socket path as a Path object."""
        return Path(self.session_socket)
