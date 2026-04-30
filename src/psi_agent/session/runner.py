"""Core session runner - message processing and tool call handling."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import AsyncGenerator
from typing import Any

import aiohttp
import anyio
from loguru import logger

from psi_agent.session.config import SessionConfig
from psi_agent.session.history import initialize_history, persist_history
from psi_agent.session.schedule import Schedule, ScheduleExecutor, load_schedule
from psi_agent.session.tool_executor import execute_tools_parallel
from psi_agent.session.tool_loader import detect_and_update_tools, load_all_tools
from psi_agent.session.types import History, ToolRegistry
from psi_agent.session.workspace_watcher import ChangeSummary, WorkspaceWatcher


def format_thinking_block(content: str) -> str:
    """Format content as a thinking block.

    Args:
        content: The thinking content to format.

    Returns:
        Formatted thinking block string.
    """
    return f"<thinking>\n{content}\n</thinking>"


def format_tool_call_thinking(
    tool_name: str,
    arguments: str,
    result: str,
) -> str:
    """Format tool call information as thinking content.

    Args:
        tool_name: Name of the tool called.
        arguments: JSON string of tool arguments.
        result: Result from tool execution.

    Returns:
        Formatted thinking block for the tool call.
    """
    content = f"[Tool: {tool_name}]\nArguments: {arguments}\nResult: {result}"
    return format_thinking_block(content)


async def _load_system(workspace: anyio.Path) -> Any:
    """Load System class from workspace systems.

    Args:
        workspace: Path to workspace directory.

    Returns:
        System instance, or None if not available.
    """
    system_file = workspace / "systems" / "system.py"
    if not await system_file.exists():
        logger.debug("No systems/system.py found, skipping system prompt")
        return None

    try:
        # Dynamic import
        spec = importlib.util.spec_from_file_location("system", system_file)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create spec for {system_file}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules["system"] = module
        spec.loader.exec_module(module)

        # Check for System class
        if not hasattr(module, "System"):
            logger.warning("No System class in system.py")
            return None

        # Instantiate System class
        system_instance = module.System(workspace)
        logger.debug("Loaded System instance from workspace")
        return system_instance

    except Exception as e:
        logger.error(f"Failed to load System class: {e}")
        return None


async def load_system_prompt(workspace: anyio.Path) -> str | None:
    """Load system prompt from workspace systems.

    Args:
        workspace: Path to workspace directory.

    Returns:
        System prompt string, or None if not available.
    """
    system_file = workspace / "systems" / "system.py"
    if not await system_file.exists():
        logger.debug("No systems/system.py found, skipping system prompt")
        return None

    try:
        # Dynamic import
        spec = importlib.util.spec_from_file_location("system", system_file)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create spec for {system_file}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules["system"] = module
        spec.loader.exec_module(module)

        # Call build_system_prompt
        if not hasattr(module, "build_system_prompt"):
            logger.warning("No build_system_prompt function in system.py")
            return None

        system_prompt = await module.build_system_prompt()
        logger.debug("Loaded system prompt from workspace")
        return system_prompt

    except Exception as e:
        logger.error(f"Failed to load system prompt: {e}")
        return None


class SessionRunner:
    """Core session runner handling message flow and tool calls."""

    def __init__(self, config: SessionConfig) -> None:
        """Initialize session runner.

        Args:
            config: Session configuration.
        """
        self.config = config
        self.registry = ToolRegistry()
        self.history: History | None = None
        self.client: aiohttp.ClientSession | None = None
        self._system_prompt_cache: str | None = None
        self._watcher: WorkspaceWatcher | None = None
        self._schedule_executor: ScheduleExecutor | None = None
        self._system: Any = None  # System instance from workspace
        self._workspace: anyio.Path | None = None  # Cached resolved workspace path

    async def __aenter__(self) -> SessionRunner:
        """Initialize session resources."""
        # Resolve and cache workspace path
        self._workspace = await self.config.workspace_path()

        # Initialize history
        self.history = await initialize_history(self.config.history_file)

        # Initialize workspace watcher with resolved absolute path
        self._watcher = WorkspaceWatcher(self._workspace)
        await self._watcher.initialize()

        # Load tools
        tools_dir = await self.config.tools_dir()
        await load_all_tools(tools_dir, self.registry)
        logger.info(f"Loaded {len(self.registry.tools)} tools")

        # Load System instance with resolved absolute path
        self._system = await _load_system(self._workspace)

        # Load system prompt
        if self._system is not None:
            self._system_prompt_cache = await self._system.build_system_prompt()
        else:
            self._system_prompt_cache = None

        # Initialize HTTP client for psi-ai
        connector = aiohttp.UnixConnector(path=str(self.config.ai_socket_path()))
        self.client = aiohttp.ClientSession(connector=connector)
        logger.debug(f"Initialized client for AI socket: {self.config.ai_socket}")

        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Clean up session resources."""
        if self.client is not None:
            await self.client.close()
            self.client = None
            logger.debug("Closed AI client")

    def set_schedule_executor(self, executor: ScheduleExecutor) -> None:
        """Set the schedule executor for hot-reload updates.

        Args:
            executor: The schedule executor instance.
        """
        self._schedule_executor = executor

    async def _handle_workspace_changes(self, changes: ChangeSummary) -> None:
        """Handle detected workspace changes.

        Args:
            changes: Summary of detected changes.
        """
        # Handle tool changes
        if changes.tools_changed:
            tools_dir = await self.config.tools_dir()
            await detect_and_update_tools(tools_dir, self.registry)

        # Handle skill/schedule changes - rebuild system prompt
        if changes.skills_changed or changes.schedules_changed:
            logger.info("Rebuilding system prompt due to workspace changes")
            if self._system is not None:
                self._system_prompt_cache = await self._system.build_system_prompt()
            else:
                self._system_prompt_cache = None

        # Handle schedule changes
        if changes.schedules_changed and self._schedule_executor is not None:
            # Use cached resolved workspace path
            workspace = self._workspace or await self.config.workspace_path()
            schedules_dir = workspace / "schedules"

            # Load new/modified schedules
            for name in changes.schedules_added + changes.schedules_modified:
                task_dir = schedules_dir / name
                schedule = await self._load_single_schedule(task_dir)
                if schedule is not None:
                    if name in changes.schedules_added:
                        await self._schedule_executor.add_schedule(schedule)
                    else:
                        await self._schedule_executor.update_schedule(schedule)

            # Remove deleted schedules
            for name in changes.schedules_removed:
                await self._schedule_executor.remove_schedule(name)

    async def _load_single_schedule(self, task_dir: anyio.Path) -> Schedule | None:
        """Load a single schedule from a task directory.

        Args:
            task_dir: Path to the task directory containing TASK.md.

        Returns:
            Schedule object, or None if invalid.
        """
        return await load_schedule(task_dir)

    async def _complete_fn(self, messages: list[dict[str, Any]]) -> str:
        """Complete function for LLM-based summarization.

        Args:
            messages: Messages to send to LLM for single-turn completion.

        Returns:
            LLM response string.
        """
        assert self.client is not None

        request_body = {
            "model": "session",  # Model is determined by psi-ai
            "messages": messages,
        }

        async with self.client.post(
            "http://localhost/v1/chat/completions",
            json=request_body,
        ) as response:
            if response.status != 200:
                text = await response.text()
                logger.error(f"Complete fn request failed: {response.status} - {text}")
                return ""

            result = await response.json()
            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            return message.get("content", "")

    async def process_request(self, user_message: dict[str, Any]) -> dict[str, Any]:
        """Process a user request and return response.

        Args:
            user_message: User message dict with role and content.

        Returns:
            Response dict in OpenAI format.

        Raises:
            aiohttp.ClientError: If communication with AI component fails.
        """
        assert self.history is not None
        assert self.client is not None

        # Check for workspace changes
        if self._watcher is not None:
            changes = await self._watcher.check_for_changes()
            if changes.has_changes:
                await self._handle_workspace_changes(changes)

        # Add user message to history
        self.history.add_message(user_message)

        # Build messages for LLM
        messages = await self._build_messages()

        # Call psi-ai and handle tool calls
        response = await self._run_conversation(messages)

        # Persist history
        await persist_history(self.history)

        return response

    async def _build_messages(self) -> list[dict[str, Any]]:
        """Build messages list for LLM request.

        Returns:
            List of messages including system prompt and history.
        """
        assert self.history is not None

        messages = []

        # Add system prompt if available
        if self._system_prompt_cache:
            messages.append({"role": "system", "content": self._system_prompt_cache})

        # Compact history if System instance is available
        if self._system is not None:
            compacted = await self._system.compact_history(
                self.history.messages,
                self._complete_fn,
            )
            messages.extend(compacted)
        else:
            # Add history without compaction
            messages.extend(self.history.messages)

        return messages

    async def _run_conversation(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Run conversation with LLM, handling tool calls.

        Uses streaming internally for better error detection and unified handling.

        Args:
            messages: Messages to send to LLM.

        Returns:
            Final response from LLM with thinking content prepended.
        """
        assert self.client is not None
        assert self.history is not None

        current_messages = list(messages)
        thinking_blocks: list[str] = []

        while True:
            # Build request with streaming enabled
            request_body = {
                "model": "session",  # Model is determined by psi-ai
                "messages": current_messages,
                "tools": self.registry.list_tools(),
                "stream": True,
            }
            logger.debug(
                f"AI request body: {json.dumps(request_body, ensure_ascii=False, indent=2)}"
            )

            # Call psi-ai with streaming
            async with self.client.post(
                "http://localhost/v1/chat/completions",
                json=request_body,
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"AI request failed: {response.status} - {text}")
                    return self._make_error_response(f"AI request failed: {text}")

                # Collect streaming response
                content_chunks = []
                tool_calls_data = []
                async for line in response.content:
                    line_str = line.decode().strip()
                    if not line_str or line_str == "data: [DONE]":
                        continue
                    if line_str.startswith("data: "):
                        try:
                            chunk = json.loads(line_str[6:])
                            delta = chunk.get("choices", [{}])[0].get("delta", {})

                            content = delta.get("content")
                            if content is not None:
                                content_chunks.append(content)
                                logger.debug(f"Stream content chunk: {content}")

                            tool_calls = delta.get("tool_calls")
                            if tool_calls is not None:
                                tool_calls_data.extend(tool_calls)
                                for tc in tool_calls:
                                    func = tc.get("function", {})
                                    name = func.get("name")
                                    args = func.get("arguments")
                                    if name is not None or args is not None:
                                        logger.debug(f"Stream tool_call: name={name}, args={args}")
                        except json.JSONDecodeError:
                            pass

            # Check if we have tool calls
            if tool_calls_data:
                # Reconstruct tool calls from streaming data
                tool_calls = self._reconstruct_tool_calls(tool_calls_data)

                # Add assistant message to history
                assistant_message = {
                    "role": "assistant",
                    "content": "".join(content_chunks) or None,
                    "tool_calls": tool_calls,
                }
                self.history.add_message(assistant_message)

                # Execute tools
                tool_messages = await execute_tools_parallel(self.registry, tool_calls)

                # Generate thinking blocks for each tool call
                for i, tool_call in enumerate(tool_calls):
                    tool_name = tool_call.get("function", {}).get("name", "unknown")
                    arguments = tool_call.get("function", {}).get("arguments", "{}")
                    # Get corresponding tool result
                    if i < len(tool_messages):
                        tool_result = tool_messages[i].get("content", "")
                    else:
                        tool_result = ""
                    thinking_block = format_tool_call_thinking(tool_name, arguments, tool_result)
                    thinking_blocks.append(thinking_block)

                # Add tool results to history and current messages
                for tool_msg in tool_messages:
                    self.history.add_message(tool_msg)
                    current_messages.append(assistant_message)
                    current_messages.append(tool_msg)

                logger.debug(f"Executed {len(tool_calls)} tool calls, continuing conversation")
                continue

            # No tool calls - we're done
            final_content = "".join(content_chunks)
            self.history.add_message({"role": "assistant", "content": final_content})

            # Prepend thinking blocks to final content
            if thinking_blocks:
                thinking_content = "\n".join(thinking_blocks) + "\n"
                final_content = thinking_content + final_content

            # Return as non-streaming response format
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": final_content,
                        },
                        "finish_reason": "stop",
                    }
                ]
            }

    def _make_error_response(self, error: str) -> dict[str, Any]:
        """Create an OpenAI-format error response.

        Args:
            error: Error message.

        Returns:
            Error response dict.
        """
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"Error: {error}",
                    },
                    "finish_reason": "stop",
                }
            ]
        }

    async def process_streaming_request(self, user_message: dict[str, Any]) -> AsyncGenerator[str]:
        """Process a user request with streaming response.

        Args:
            user_message: User message dict with role and content.

        Returns:
            Async generator yielding SSE chunks.
        """
        assert self.history is not None
        assert self.client is not None

        # Check for workspace changes
        if self._watcher is not None:
            changes = await self._watcher.check_for_changes()
            if changes.has_changes:
                await self._handle_workspace_changes(changes)

        # Add user message to history
        self.history.add_message(user_message)

        # Build messages for LLM
        messages = await self._build_messages()

        # Stream the conversation
        return self._stream_conversation(messages)

    async def _stream_conversation(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str]:
        """Stream conversation with thinking blocks.

        Args:
            messages: Messages to send to LLM.

        Yields:
            SSE formatted strings including thinking blocks and final content.
        """
        assert self.client is not None
        assert self.history is not None

        current_messages = list(messages)

        while True:
            # Build request
            request_body = {
                "model": "session",
                "messages": current_messages,
                "tools": self.registry.list_tools(),
                "stream": True,
            }

            # Call psi-ai with streaming
            async with self.client.post(
                "http://localhost/v1/chat/completions",
                json=request_body,
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"AI request failed: {response.status} - {text}")
                    # Yield error as SSE
                    error_content = f"Error: AI request failed: {text}"
                    error_data = {
                        "choices": [{"delta": {"content": error_content}, "finish_reason": "stop"}]
                    }
                    data = json.dumps(error_data)
                    yield f"data: {data}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                # Collect streaming response
                content_chunks = []
                tool_calls_data = []
                async for line in response.content:
                    line_str = line.decode().strip()
                    if not line_str or line_str == "data: [DONE]":
                        continue
                    if line_str.startswith("data: "):
                        try:
                            chunk = json.loads(line_str[6:])
                            delta = chunk.get("choices", [{}])[0].get("delta", {})

                            # Stream reasoning field directly if present
                            reasoning = delta.get("reasoning")
                            if reasoning:
                                logger.debug(f"Stream reasoning chunk: {reasoning}")
                                reasoning_data = {
                                    "choices": [
                                        {"delta": {"reasoning": reasoning}, "finish_reason": None}
                                    ]
                                }
                                yield f"data: {json.dumps(reasoning_data)}\n\n"

                            # Stream content field directly if present
                            content = delta.get("content")
                            if content is not None:
                                content_chunks.append(content)
                                if content:  # Only log non-empty content
                                    logger.debug(f"Stream content chunk: {content}")
                                content_data = {
                                    "choices": [
                                        {"delta": {"content": content}, "finish_reason": None}
                                    ]
                                }
                                yield f"data: {json.dumps(content_data)}\n\n"

                            tool_calls = delta.get("tool_calls")
                            if tool_calls is not None:
                                tool_calls_data.extend(tool_calls)
                                for tc in tool_calls:
                                    func = tc.get("function", {})
                                    name = func.get("name")
                                    args = func.get("arguments")
                                    if name is not None or args is not None:
                                        logger.debug(f"Stream tool_call: name={name}, args={args}")
                        except json.JSONDecodeError:
                            pass

            # Check if we have tool calls
            if tool_calls_data:
                # Reconstruct tool calls from streaming data
                tool_calls = self._reconstruct_tool_calls(tool_calls_data)

                # Add assistant message to history
                assistant_message = {
                    "role": "assistant",
                    "content": "".join(content_chunks) or None,
                    "tool_calls": tool_calls,
                }
                self.history.add_message(assistant_message)

                # Execute tools
                tool_messages = await execute_tools_parallel(self.registry, tool_calls)

                # Yield tool call information as reasoning field
                for i, tool_call in enumerate(tool_calls):
                    tool_name = tool_call.get("function", {}).get("name", "unknown")
                    arguments = tool_call.get("function", {}).get("arguments", "{}")
                    if i < len(tool_messages):
                        tool_result = tool_messages[i].get("content", "")
                    else:
                        tool_result = ""

                    # Format tool call info without thinking tags
                    tool_info = (
                        f"[Tool: {tool_name}]\nArguments: {arguments}\nResult: {tool_result}"
                    )
                    logger.debug(f"Stream tool call reasoning: {tool_info}")

                    # Yield as reasoning field
                    reasoning_data = {
                        "choices": [{"delta": {"reasoning": tool_info}, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(reasoning_data)}\n\n"

                # Add tool results to history and current messages
                for tool_msg in tool_messages:
                    self.history.add_message(tool_msg)
                    current_messages.append(assistant_message)
                    current_messages.append(tool_msg)

                logger.debug(f"Executed {len(tool_calls)} tool calls, continuing conversation")
                continue

            # No tool calls - stream final response
            final_content = "".join(content_chunks)
            self.history.add_message({"role": "assistant", "content": final_content})
            await persist_history(self.history)

            # Yield final content (already yielded during streaming, just send done)
            yield "data: [DONE]\n\n"
            return

    def _reconstruct_tool_calls(
        self, tool_calls_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Reconstruct tool calls from streaming chunks.

        Args:
            tool_calls_data: List of tool call delta chunks.

        Returns:
            List of complete tool call dicts.
        """
        # Group by index and merge
        tool_calls_map: dict[int, dict[str, Any]] = {}

        for chunk in tool_calls_data:
            index = chunk.get("index", 0)
            if index not in tool_calls_map:
                tool_calls_map[index] = {
                    "id": "",
                    "type": "function",
                    "function": {"name": "", "arguments": ""},
                }

            if "id" in chunk:
                tool_calls_map[index]["id"] = chunk["id"]
            if "function" in chunk:
                func = chunk["function"]
                if func.get("name") is not None:
                    tool_calls_map[index]["function"]["name"] += func["name"]
                if func.get("arguments") is not None:
                    tool_calls_map[index]["function"]["arguments"] += func["arguments"]

        return list(tool_calls_map.values())
