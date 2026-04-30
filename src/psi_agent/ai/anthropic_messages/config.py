"""Configuration for Anthropic Messages server."""

from __future__ import annotations

from dataclasses import dataclass

import anyio


@dataclass
class AnthropicMessagesConfig:
    """Configuration for the Anthropic Messages server.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        model: The model name to use for messages (e.g., "claude-sonnet-4-20250514").
        api_key: The API key for authentication.
        base_url: The base URL for the Anthropic API.
        max_tokens: The maximum number of tokens to generate (default: 4096).
        thinking: Thinking mode type (e.g., "enabled", "disabled").
            None means no parameter.
        reasoning_effort: Reasoning effort level (e.g., "low", "medium", "high").
            None means no parameter.
    """

    session_socket: str
    model: str
    api_key: str
    base_url: str = "https://api.anthropic.com"
    max_tokens: int = 4096
    thinking: str | None = None
    reasoning_effort: str | None = None

    def socket_path(self) -> anyio.Path:
        """Get the socket path as a Path object."""
        return anyio.Path(self.session_socket)
