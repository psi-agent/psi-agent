"""Tests for tool_executor module."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from psi_agent.session.tool_executor import execute_tool, execute_tools_parallel
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


@pytest.mark.asyncio
async def test_execute_tool_exception():
    """Test tool that raises exception."""

    async def failing_tool() -> str:
        raise ValueError("Tool failed!")

    registry = ToolRegistry()
    registry.tools["failing"] = ToolSchema(
        name="failing",
        schema={"type": "function", "function": {"name": "failing"}},
        func=failing_tool,
        file_hash="hash",
    )

    result = await execute_tool(registry, "failing", {})
    assert "Error" in result
    assert "Tool failed!" in result


@pytest.mark.asyncio
async def test_execute_tools_parallel_single(registry):
    """Test parallel execution with single tool call."""
    tool_calls = [
        {
            "id": "call_1",
            "function": {"name": "sample", "arguments": '{"name": "Test"}'},
        }
    ]

    results = await execute_tools_parallel(registry, tool_calls)

    assert len(results) == 1
    assert results[0]["role"] == "tool"
    assert results[0]["tool_call_id"] == "call_1"
    assert "Hello Test" in results[0]["content"]


@pytest.mark.asyncio
async def test_execute_tools_parallel_multiple(registry):
    """Test parallel execution with multiple tool calls."""
    tool_calls = [
        {
            "id": "call_1",
            "function": {"name": "sample", "arguments": '{"name": "First"}'},
        },
        {
            "id": "call_2",
            "function": {"name": "sample", "arguments": '{"name": "Second"}'},
        },
    ]

    results = await execute_tools_parallel(registry, tool_calls)

    assert len(results) == 2
    assert results[0]["tool_call_id"] == "call_1"
    assert results[1]["tool_call_id"] == "call_2"


@pytest.mark.asyncio
async def test_execute_tools_parallel_invalid_arguments(registry):
    """Test parallel execution with invalid JSON arguments."""
    tool_calls = [
        {
            "id": "call_1",
            "function": {"name": "sample", "arguments": "not valid json"},
        }
    ]

    # Should not raise, but use empty arguments
    results = await execute_tools_parallel(registry, tool_calls)

    assert len(results) == 1
    # Tool will be called with empty arguments, which may fail or use defaults


@pytest.mark.asyncio
async def test_execute_tools_parallel_mixed_success_failure():
    """Test parallel execution with some tools failing."""
    registry = ToolRegistry()

    async def good_tool() -> str:
        return "success"

    async def bad_tool() -> str:
        raise RuntimeError("failed")

    registry.tools["good"] = ToolSchema(
        name="good",
        schema={"type": "function", "function": {"name": "good"}},
        func=good_tool,
        file_hash="hash1",
    )
    registry.tools["bad"] = ToolSchema(
        name="bad",
        schema={"type": "function", "function": {"name": "bad"}},
        func=bad_tool,
        file_hash="hash2",
    )

    tool_calls = [
        {"id": "call_1", "function": {"name": "good", "arguments": "{}"}},
        {"id": "call_2", "function": {"name": "bad", "arguments": "{}"}},
    ]

    results = await execute_tools_parallel(registry, tool_calls)

    assert len(results) == 2
    assert results[0]["content"] == "success"
    assert "Error" in results[1]["content"]


class TestExecuteToolExceptions:
    """Exception tests for execute_tool."""

    @pytest.mark.asyncio
    async def test_tool_raising_type_error(self) -> None:
        """Tool raising TypeError (argument mismatch)."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="bad_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "bad_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(side_effect=TypeError("missing required argument")),
            file_hash="hash",
        )
        registry.register(schema)

        result = await execute_tool(registry, "bad_tool", {})
        assert "error" in result.lower() or "type" in result.lower() or "argument" in result.lower()

    @pytest.mark.asyncio
    async def test_tool_returning_none(self) -> None:
        """Tool returning None."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="none_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "none_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(return_value=None),
            file_hash="hash",
        )
        registry.register(schema)

        result = await execute_tool(registry, "none_tool", {})
        assert result is None or result == "" or result == "None" or result == "null"

    @pytest.mark.asyncio
    async def test_tool_returning_empty_string(self) -> None:
        """Tool returning empty string."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="empty_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "empty_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(return_value=""),
            file_hash="hash",
        )
        registry.register(schema)

        result = await execute_tool(registry, "empty_tool", {})
        assert result == ""

    @pytest.mark.asyncio
    async def test_tool_returning_dict(self) -> None:
        """Tool returning a dict (non-string type)."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="dict_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "dict_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(return_value={"key": "value"}),
            file_hash="hash",
        )
        registry.register(schema)

        result = await execute_tool(registry, "dict_tool", {})
        assert isinstance(result, str)
        assert "key" in result

    @pytest.mark.asyncio
    async def test_tool_returning_list(self) -> None:
        """Tool returning a list (non-string type)."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="list_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "list_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(return_value=[1, 2, 3]),
            file_hash="hash",
        )
        registry.register(schema)

        result = await execute_tool(registry, "list_tool", {})
        assert isinstance(result, str)


class TestExecuteToolsParallelBoundary:
    """Boundary tests for execute_tools_parallel."""

    @pytest.mark.asyncio
    async def test_empty_tool_calls_list(self) -> None:
        """Empty tool_calls list returns empty results."""
        registry = ToolRegistry()
        result = await execute_tools_parallel(registry, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_tool_call_missing_function_field(self) -> None:
        """Tool call with missing function field."""
        registry = ToolRegistry()
        tool_calls = [{"id": "call_1", "type": "function"}]
        result = await execute_tools_parallel(registry, tool_calls)
        assert len(result) == 1
        assert "error" in result[0].get("content", "").lower() or result[0].get("content", "") == ""

    @pytest.mark.asyncio
    async def test_tool_call_missing_id_field(self) -> None:
        """Tool call with missing id field."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="test_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(return_value="ok"),
            file_hash="hash",
        )
        registry.register(schema)

        tool_calls = [{"type": "function", "function": {"name": "test_tool", "arguments": "{}"}}]
        result = await execute_tools_parallel(registry, tool_calls)
        assert len(result) == 1
        assert result[0] is not None

    @pytest.mark.asyncio
    async def test_all_tool_calls_failing(self) -> None:
        """All tool calls failing."""
        registry = ToolRegistry()
        schema = ToolSchema(
            name="fail_tool",
            schema={
                "type": "function",
                "function": {
                    "name": "fail_tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            func=AsyncMock(side_effect=RuntimeError("Tool failed")),
            file_hash="hash",
        )
        registry.register(schema)

        tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "fail_tool", "arguments": "{}"},
            },
            {
                "id": "call_2",
                "type": "function",
                "function": {"name": "fail_tool", "arguments": "{}"},
            },
        ]
        result = await execute_tools_parallel(registry, tool_calls)
        assert len(result) == 2
        for r in result:
            assert "error" in r.get("content", "").lower() or "fail" in r.get("content", "").lower()
