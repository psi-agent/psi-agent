"""psi-channel: Channel components for psi-agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from tyro.conf import OmitSubcommandPrefixes

__all__ = ["Commands"]


@dataclass
class Commands:
    """Channel commands."""

    subcommand: Annotated[Cli | Repl, OmitSubcommandPrefixes]

    def __call__(self) -> None:
        self.subcommand()


# Import after class definition to avoid circular imports
from psi_agent.channel.cli.cli import Cli  # noqa: E402
from psi_agent.channel.repl.cli import Repl  # noqa: E402
