"""Configuration for psi-session."""

from __future__ import annotations

from dataclasses import dataclass

import anyio


@dataclass
class SessionConfig:
    """Configuration for psi-session.

    Args:
        channel_socket: Path to the Unix socket for communication with channel.
        ai_socket: Path to the Unix socket for communication with psi-ai.
        workspace: Path to the workspace directory containing tools/skills/systems.
        history_file: Optional path to JSON file for history persistence.
    """

    channel_socket: str
    ai_socket: str
    workspace: str
    history_file: str | None = None

    def channel_socket_path(self) -> anyio.Path:
        """Get channel socket path as Path object."""
        return anyio.Path(self.channel_socket)

    def ai_socket_path(self) -> anyio.Path:
        """Get AI socket path as Path object."""
        return anyio.Path(self.ai_socket)

    def workspace_path(self) -> anyio.Path:
        """Get workspace path as Path object."""
        return anyio.Path(self.workspace)

    def history_file_path(self) -> anyio.Path | None:
        """Get history file path as Path object, or None."""
        return anyio.Path(self.history_file) if self.history_file else None

    def tools_dir(self) -> anyio.Path:
        """Get tools directory path."""
        return self.workspace_path() / "tools"

    def systems_dir(self) -> anyio.Path:
        """Get systems directory path."""
        return self.workspace_path() / "systems"
