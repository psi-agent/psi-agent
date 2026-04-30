"""Configuration for OpenAI completions server."""

from __future__ import annotations

from dataclasses import dataclass

import anyio


@dataclass
class OpenAICompletionsConfig:
    """Configuration for the OpenAI completions server.

    Args:
        session_socket: Path to the Unix socket for communication with psi-session.
        model: The model name to use for completions.
        api_key: The API key for authentication.
        base_url: The base URL for the OpenAI-compatible API.
        thinking: Thinking mode type (e.g., "enabled", "disabled").
            None means no parameter.
        reasoning_effort: Reasoning effort level (e.g., "low", "medium", "high").
            None means no parameter.
    """

    session_socket: str
    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    thinking: str | None = None
    reasoning_effort: str | None = None

    def socket_path(self) -> anyio.Path:
        """Get the socket path as a Path object."""
        return anyio.Path(self.session_socket)
