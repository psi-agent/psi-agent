"""Tests for tool_executor module."""

import pytest

from psi_agent.session.tool_executor import execute_tool
from psi_agent.session.types import ToolRegistry, ToolSchema


async def sample_tool(name: str, count: int = 1) -> str:
    """Sample tool for testing.

    Args:
        name: The name parameter.
        count: The count parameter.

    Returns:
        Result string.
    """
    return f"Hello {name}, count={count}"


@pytest.fixture
def registry():
    """Create a test registry with sample tool."""
    registry = ToolRegistry()
    tool = ToolSchema(
        name="sample",
        schema={
            "type": "function",
            "function": {
                "name": "sample",
                "description": "Sample tool for testing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The name parameter."},
                        "count": {"type": "integer", "description": "The count parameter."},
                    },
                    "required": ["name"],
                },
            },
        },
        func=sample_tool,
        file_hash="test_hash",
    )
    registry.register(tool)
    return registry


@pytest.mark.asyncio
async def test_execute_tool_success(registry):
    """Test successful tool execution."""
    result = await execute_tool(registry, "sample", {"name": "World", "count": 5})
    assert result == "Hello World, count=5"


@pytest.mark.asyncio
async def test_execute_tool_default_args(registry):
    """Test tool execution with default arguments."""
    result = await execute_tool(registry, "sample", {"name": "Test"})
    assert result == "Hello Test, count=1"


@pytest.mark.asyncio
async def test_execute_tool_not_found(registry):
    """Test tool not found error."""
    result = await execute_tool(registry, "nonexistent", {})
    assert "Error" in result
    assert "not found" in result


@pytest.mark.asyncio
async def test_execute_tool_complex_result(registry):
    """Test tool returning complex type (JSON serialization)."""

    async def complex_tool() -> dict:
        return {"key": "value", "nested": {"a": 1}}

    registry.tools["complex"] = ToolSchema(
        name="complex",
        schema={"type": "function", "function": {"name": "complex"}},
        func=complex_tool,
        file_hash="hash",
    )

    result = await execute_tool(registry, "complex", {})
    assert '{"key": "value"' in result
