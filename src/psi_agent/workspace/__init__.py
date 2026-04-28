"""Workspace management components for psi-agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from tyro.conf import OmitSubcommandPrefixes

from psi_agent.workspace.manifest import Layer, Manifest

__all__ = ["Manifest", "Layer", "Commands"]


@dataclass
class Commands:
    """Workspace commands."""

    subcommand: Annotated[Pack | Unpack | Mount | Umount | Snapshot, OmitSubcommandPrefixes]

    def __call__(self) -> None:
        self.subcommand()


# Import after class definition to avoid circular imports
from psi_agent.workspace.mount.cli import Mount  # noqa: E402
from psi_agent.workspace.pack.cli import Pack  # noqa: E402
from psi_agent.workspace.snapshot.cli import Snapshot  # noqa: E402
from psi_agent.workspace.umount.cli import Umount  # noqa: E402
from psi_agent.workspace.unpack.cli import Unpack  # noqa: E402
