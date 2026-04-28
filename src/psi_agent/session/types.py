"""Type definitions for psi-session."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolSchema:
    """OpenAI tool schema with execution metadata.

    Attributes:
        name: Tool name (from file name).
        schema: OpenAI function schema (type, function dict).
        func: The async tool function to execute.
        file_hash: MD5 hash of the source file for update detection.
    """

    name: str
    schema: dict[str, Any]
    func: Callable[..., Coroutine[Any, Any, Any]]
    file_hash: str


@dataclass
class ToolRegistry:
    """Registry for dynamically loaded tools.

    Attributes:
        tools: Mapping from tool name to ToolSchema.
    """

    tools: dict[str, ToolSchema] = field(default_factory=dict)

    def get(self, name: str) -> ToolSchema | None:
        """Get tool by name.

        Args:
            name: Tool name.

        Returns:
            ToolSchema if found, None otherwise.
        """
        return self.tools.get(name)

    def register(self, tool: ToolSchema) -> None:
        """Register a tool.

        Args:
            tool: ToolSchema to register.
        """
        self.tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """Unregister a tool.

        Args:
            name: Tool name to unregister.
        """
        self.tools.pop(name, None)

    def clear(self) -> None:
        """Clear all registered tools."""
        self.tools.clear()

    def list_tools(self) -> list[dict[str, Any]]:
        """List all tool schemas in OpenAI format.

        Returns:
            List of OpenAI tool schemas.
        """
        return [tool.schema for tool in self.tools.values()]


@dataclass
class History:
    """Conversation history management.

    Attributes:
        messages: List of conversation messages.
        history_file: Optional path to JSON persistence file.
    """

    messages: list[dict[str, Any]] = field(default_factory=list)
    history_file: str | None = None

    def add_message(self, message: dict[str, Any]) -> None:
        """Add a message to history.

        Args:
            message: Message dict with role and content.
        """
        self.messages.append(message)

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
