"""psi-session: Agent session component for psi-agent."""

from __future__ import annotations

from psi_agent.session.cli import Session, main
from psi_agent.session.config import SessionConfig
from psi_agent.session.runner import SessionRunner
from psi_agent.session.server import SessionServer
from psi_agent.session.types import History, ToolRegistry, ToolSchema

__all__ = [
    "main",
    "Session",
    "SessionConfig",
    "SessionRunner",
    "SessionServer",
    "History",
    "ToolRegistry",
    "ToolSchema",
    "Commands",
]

# Session is a single command, so Commands is just an alias
Commands = Session
