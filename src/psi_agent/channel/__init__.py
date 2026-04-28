"""psi-channel: Channel components for psi-agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from tyro.conf import OmitSubcommandPrefixes

from psi_agent.channel.cli.cli import Cli
from psi_agent.channel.repl.cli import Repl
from psi_agent.channel.telegram.cli import Telegram

__all__ = ["Commands"]


@dataclass
class Commands:
    """Channel commands."""

    subcommand: Annotated[Cli | Repl | Telegram, OmitSubcommandPrefixes]

    def __call__(self) -> None:
        self.subcommand()
