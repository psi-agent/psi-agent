"""Workspace management components for psi-agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from tyro.conf import OmitSubcommandPrefixes

from psi_agent.workspace.manifest import Layer, Manifest
from psi_agent.workspace.mount.cli import Mount
from psi_agent.workspace.pack.cli import Pack
from psi_agent.workspace.snapshot.cli import Snapshot
from psi_agent.workspace.umount.cli import Umount
from psi_agent.workspace.unpack.cli import Unpack

__all__ = ["Manifest", "Layer", "Commands"]


@dataclass
class Commands:
    """Workspace commands."""

    subcommand: Annotated[Pack | Unpack | Mount | Umount | Snapshot, OmitSubcommandPrefixes]

    def __call__(self) -> None:
        self.subcommand()
