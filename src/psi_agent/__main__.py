"""Central CLI entry point for psi-agent.

This module provides a unified CLI that uses tyro's native subcommand support
for all component CLIs. This enables `uvx psi-agent` to work seamlessly
without requiring users to clone the repository.

Usage:
    uvx psi-agent ai openai-completions --session-socket ./sock ...
    uvx psi-agent channel cli --session-socket ./sock ...
    uvx psi-agent session --channel-socket ./sock ...
    uvx psi-agent workspace pack --input ./workspace ...
"""

from __future__ import annotations

from typing import Annotated

import tyro
from tyro.conf import subcommand

from psi_agent.ai import Commands as AiCommands
from psi_agent.channel import Commands as ChannelCommands
from psi_agent.session import Commands as SessionCommands
from psi_agent.workspace import Commands as WorkspaceCommands


def main() -> None:
    """Main entry point for psi-agent CLI."""
    # Build Union type with explicit subcommand names
    top_commands = (
        Annotated[AiCommands, subcommand("ai")]
        | Annotated[ChannelCommands, subcommand("channel")]
        | Annotated[SessionCommands, subcommand("session")]
        | Annotated[WorkspaceCommands, subcommand("workspace")]
    )

    result = tyro.cli(top_commands, prog_name="psi-agent")
    result()


if __name__ == "__main__":
    main()
