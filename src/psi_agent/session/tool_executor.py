"""Tool execution and result formatting."""

import json
from typing import Any

from loguru import logger

from psi_agent.session.types import ToolRegistry


async def execute_tool(
    registry: ToolRegistry,
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """Execute a tool with given arguments.

    Args:
        registry: ToolRegistry containing the tool.
        tool_name: Name of the tool to execute.
        arguments: Arguments to pass to the tool function.

    Returns:
        Tool result as string (JSON for complex types).
    """
    tool_schema = registry.get(tool_name)
    if tool_schema is None:
        logger.error(f"Tool not found: {tool_name}")
        return f"Error: Tool '{tool_name}' not found"

    logger.debug(f"Executing tool: {tool_name} with arguments: {arguments}")

    try:
        result = await tool_schema.func(**arguments)

        # Format result for LLM
        if isinstance(result, str):
            return result
        else:
            return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Tool execution failed: {tool_name}: {e}")
        return f"Error: {e}"


async def execute_tools_parallel(
    registry: ToolRegistry,
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Execute multiple tool calls in parallel.

    Args:
        registry: ToolRegistry containing tools.
        tool_calls: List of tool call dicts with 'function.name' and 'function.arguments'.

    Returns:
        List of tool result messages ready for LLM.
    """
    import asyncio

    tasks = []
    tool_call_ids = []

    for tool_call in tool_calls:
        function = tool_call.get("function", {})
        tool_name = function.get("name", "")
        arguments_str = function.get("arguments", "{}")
        call_id = tool_call.get("id", "")

        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse arguments: {arguments_str}")
            arguments = {}

        tasks.append(execute_tool(registry, tool_name, arguments))
        tool_call_ids.append(call_id)

    # Execute in parallel
    results = await asyncio.gather(*tasks)

    # Format as tool result messages
    tool_messages = []
    for call_id, result in zip(tool_call_ids, results, strict=True):
        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": call_id,
                "content": result,
            }
        )

    return tool_messages
