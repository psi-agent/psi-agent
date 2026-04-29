"""Tool dynamic loading and registry management."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import re
import sys
from collections.abc import Callable, Coroutine
from typing import Any

import anyio
from loguru import logger

from psi_agent.session.types import ToolRegistry, ToolSchema


async def compute_file_hash(file_path: anyio.Path) -> str:
    """Compute MD5 hash of a file.

    Args:
        file_path: Path to the file.

    Returns:
        MD5 hash string.
    """
    content = await file_path.read_bytes()
    return hashlib.md5(content).hexdigest()


def parse_google_docstring(docstring: str) -> tuple[str, dict[str, str]]:
    """Parse Google-style docstring for description and parameter descriptions.

    Args:
        docstring: The docstring to parse.

    Returns:
        Tuple of (function_description, parameter_descriptions dict).
    """
    if not docstring:
        return "", {}

    # Extract main description (before Args:)
    desc_match = re.match(r"^([\s\S]*?)(?:Args:|$)", docstring.strip(), re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract Args section
    args_match = re.search(r"Args:\s*\n([\s\S]*?)(?:Returns:|Raises:|$)", docstring, re.DOTALL)
    param_descriptions = {}

    if args_match:
        args_text = args_match.group(1)
        # Parse each parameter line by line
        current_param = None
        current_desc = []

        for line in args_text.split("\n"):
            # Check if this is a new parameter definition
            param_match = re.match(r"^\s*(\w+):\s*(.*)$", line)
            if param_match:
                # Save previous parameter if exists
                if current_param is not None:
                    param_descriptions[current_param] = " ".join(current_desc).strip()
                current_param = param_match.group(1)
                current_desc = [param_match.group(2)]
            elif current_param is not None and line.strip():
                # Continue description on next line
                current_desc.append(line.strip())

        # Save last parameter
        if current_param is not None:
            param_descriptions[current_param] = " ".join(current_desc).strip()

    return description, param_descriptions


def python_type_to_openai_type(python_type: type | None) -> str:
    """Convert Python type to OpenAI schema type string.

    Args:
        python_type: Python type annotation.

    Returns:
        OpenAI schema type string.
    """
    if python_type is None:
        return "string"

    type_name = getattr(python_type, "__name__", str(python_type))

    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "List": "array",
        "dict": "object",
        "Dict": "object",
    }

    return type_mapping.get(type_name, "string")


def generate_tool_schema(
    func_name: str,
    func: Callable[..., Coroutine[Any, Any, Any]],
    description: str,
    param_descriptions: dict[str, str],
) -> dict[str, Any]:
    """Generate OpenAI tool schema from function signature.

    Args:
        func_name: Name of the tool.
        func: The tool function.
        description: Function description from docstring.
        param_descriptions: Parameter descriptions from docstring.

    Returns:
        OpenAI tool schema dict.
    """
    sig = inspect.signature(func)
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    for param_name, param in sig.parameters.items():
        # Skip if no annotation
        if param.annotation == inspect.Parameter.empty:
            continue

        param_type = python_type_to_openai_type(param.annotation)
        param_desc = param_descriptions.get(param_name, f"Parameter {param_name}")

        parameters["properties"][param_name] = {
            "type": param_type,
            "description": param_desc,
        }

        # Required if no default value
        if param.default == inspect.Parameter.empty:
            parameters["required"].append(param_name)

    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": description,
            "parameters": parameters,
        },
    }


async def load_tool_from_file(file_path: anyio.Path) -> ToolSchema | None:
    """Load a tool from a Python file.

    Args:
        file_path: Path to the tool .py file.

    Returns:
        ToolSchema if successful, None if failed.

    Raises:
        OSError: If file cannot be read for hash computation.
    """
    tool_name = file_path.stem
    file_hash = await compute_file_hash(file_path)

    try:
        # Dynamic import
        spec = importlib.util.spec_from_file_location(tool_name, file_path)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create spec for {file_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[tool_name] = module
        spec.loader.exec_module(module)

        # Find tool function
        if not hasattr(module, "tool"):
            logger.warning(f"No 'tool' function found in {file_path}")
            return None

        func = module.tool

        # Verify it's async
        if not inspect.iscoroutinefunction(func):
            logger.error(f"Tool function in {file_path} is not async")
            return None

        # Parse docstring
        docstring = inspect.getdoc(func) or ""
        description, param_descriptions = parse_google_docstring(docstring)

        # Generate schema
        schema = generate_tool_schema(tool_name, func, description, param_descriptions)

        logger.debug(f"Loaded tool: {tool_name} from {file_path}")

        return ToolSchema(
            name=tool_name,
            schema=schema,
            func=func,
            file_hash=file_hash,
        )

    except Exception as e:
        logger.error(f"Failed to load tool from {file_path}: {e}")
        return None


async def scan_tools_directory(tools_dir: anyio.Path) -> dict[str, tuple[anyio.Path, str]]:
    """Scan tools directory and return file info.

    Args:
        tools_dir: Path to the tools directory.

    Returns:
        Dict mapping tool name to (file_path, file_hash).
    """
    if not await tools_dir.exists():
        logger.debug(f"Tools directory does not exist: {tools_dir}")
        return {}

    tool_files: dict[str, tuple[anyio.Path, str]] = {}

    async for file_path in tools_dir.iterdir():
        if await file_path.is_file() and file_path.suffix == ".py":
            tool_name = file_path.stem
            file_hash = await compute_file_hash(file_path)
            tool_files[tool_name] = (file_path, file_hash)

    return tool_files


async def load_all_tools(tools_dir: anyio.Path, registry: ToolRegistry) -> None:
    """Load all tools from directory into registry.

    Args:
        tools_dir: Path to the tools directory.
        registry: ToolRegistry to populate.
    """
    tool_files = await scan_tools_directory(tools_dir)

    for _tool_name, (file_path, _) in tool_files.items():
        tool_schema = await load_tool_from_file(file_path)
        if tool_schema is not None:
            registry.register(tool_schema)


async def detect_and_update_tools(tools_dir: anyio.Path, registry: ToolRegistry) -> None:
    """Detect tool changes and update registry.

    Args:
        tools_dir: Path to the tools directory.
        registry: Existing ToolRegistry to update.
    """
    current_files = await scan_tools_directory(tools_dir)
    current_names = set(current_files.keys())
    registered_names = set(registry.tools.keys())

    # New tools to load
    new_tools = current_names - registered_names
    for tool_name in new_tools:
        file_path, _ = current_files[tool_name]
        tool_schema = await load_tool_from_file(file_path)
        if tool_schema is not None:
            registry.register(tool_schema)
            logger.info(f"Added new tool: {tool_name}")

    # Removed tools to unregister
    removed_tools = registered_names - current_names
    for tool_name in removed_tools:
        registry.unregister(tool_name)
        logger.info(f"Removed tool: {tool_name}")

    # Check for updates
    common_tools = current_names & registered_names
    for tool_name in common_tools:
        file_path, new_hash = current_files[tool_name]
        old_hash = registry.tools[tool_name].file_hash

        if new_hash != old_hash:
            tool_schema = await load_tool_from_file(file_path)
            if tool_schema is not None:
                registry.register(tool_schema)
                logger.info(f"Updated tool: {tool_name}")
