"""Tests for runner module."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

from psi_agent.session.config import SessionConfig
from psi_agent.session.runner import (
    SessionRunner,
    _load_system,
    format_thinking_block,
    format_tool_call_thinking,
    load_system_prompt,
)
from psi_agent.session.tool_loader import load_tool_from_file
from psi_agent.session.workspace_watcher import ChangeSummary


@pytest.fixture
def config():
    """Create test config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tools_dir = os.path.join(tmpdir, "tools")
        os.makedirs(tools_dir)

        yield SessionConfig(
            channel_socket=os.path.join(tmpdir, "channel.sock"),
            ai_socket=os.path.join(tmpdir, "ai.sock"),
            workspace=tmpdir,
            history_file=None,
        )


@pytest.mark.asyncio
async def test_load_system_prompt_no_file():
    """Test loading system prompt when no system.py exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await load_system_prompt(anyio.Path(tmpdir))
        assert result is None


@pytest.mark.asyncio
async def test_load_system_prompt_with_file():
    """Test loading system prompt from system.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = anyio.Path(tmpdir)
        systems_dir = workspace / "systems"
        await systems_dir.mkdir()

        system_file = systems_dir / "system.py"
        await system_file.write_text(
            """
async def build_system_prompt() -> str:
    return "You are a helpful assistant."
"""
        )

        result = await load_system_prompt(workspace)
        assert result == "You are a helpful assistant."


@pytest.mark.asyncio
async def test_load_system_prompt_no_function():
    """Test loading system prompt when function doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = anyio.Path(tmpdir)
        systems_dir = workspace / "systems"
        await systems_dir.mkdir()

        system_file = systems_dir / "system.py"
        await system_file.write_text("# no function here\n")

        result = await load_system_prompt(workspace)
        assert result is None


def test_session_runner_init(config):
    """Test SessionRunner initialization."""
    runner = SessionRunner(config)
    assert runner.config == config
    assert runner.registry is not None
    assert runner.history is None
    assert runner.client is None


@pytest.mark.asyncio
async def test_session_runner_context_enter(config):
    """Test SessionRunner context manager enter initializes resources."""
    runner = SessionRunner(config)
    async with runner:
        assert runner.history is not None
        assert runner.client is not None


@pytest.mark.asyncio
async def test_session_runner_context_exit_closes_client(config):
    """Test SessionRunner context manager exit closes client."""
    runner = SessionRunner(config)
    async with runner:
        client = runner.client
        assert client is not None

    # After exit, client should be None
    assert runner.client is None


@pytest.mark.asyncio
async def test_session_runner_loads_tools(config):
    """Test SessionRunner loads tools from workspace."""
    # Create a tool file
    tools_dir = config.tools_dir()
    tool_file = tools_dir / "test_tool.py"
    await tool_file.write_text(
        """
async def tool(name: str) -> str:
    '''Test tool.

    Args:
        name: The name.

    Returns:
        Greeting string.
    '''
    return f"Hello {name}"
"""
    )

    runner = SessionRunner(config)
    async with runner:
        assert len(runner.registry.tools) >= 1
        assert "test_tool" in runner.registry.tools


@pytest.mark.asyncio
async def test_process_request_adds_to_history(config):
    """Test process_request adds user message to history."""
    runner = SessionRunner(config)
    async with runner:
        # Create streaming response mock
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello!"}}]}\n',
            b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(runner.client, "post", return_value=mock_response):
            await runner.process_request({"role": "user", "content": "Hi"})

        # Check history was updated
        assert runner.history is not None
        assert len(runner.history.messages) >= 1
        assert runner.history.messages[0]["role"] == "user"


@pytest.mark.asyncio
async def test_process_request_returns_response(config):
    """Test process_request returns AI response."""
    runner = SessionRunner(config)
    async with runner:
        # Create streaming response mock
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Response text"}}]}\n',
            b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(runner.client, "post", return_value=mock_response):
            result = await runner.process_request({"role": "user", "content": "Test"})

        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Response text"


@pytest.mark.asyncio
async def test_process_request_handles_ai_error(config):
    """Test process_request handles AI request failure."""
    runner = SessionRunner(config)
    async with runner:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(runner.client, "post", return_value=mock_response):
            result = await runner.process_request({"role": "user", "content": "Test"})

        # Should return error response
        assert "choices" in result
        assert "Error" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
async def test_build_messages_includes_system_prompt(config):
    """Test _build_messages includes system prompt when available."""
    runner = SessionRunner(config)

    async with runner:
        # Set system prompt after entering context
        runner._system_prompt_cache = "You are helpful."
        # Add a message to history
        assert runner.history is not None
        runner.history.add_message({"role": "user", "content": "Hi"})

        messages = await runner._build_messages()
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are helpful."
        assert messages[1]["role"] == "user"


@pytest.mark.asyncio
async def test_make_error_response(config):
    """Test _make_error_response creates valid response."""
    runner = SessionRunner(config)

    response = runner._make_error_response("Something went wrong")

    assert "choices" in response
    assert len(response["choices"]) == 1
    assert "Error" in response["choices"][0]["message"]["content"]
    assert response["choices"][0]["finish_reason"] == "stop"


@pytest.mark.asyncio
async def test_reconstruct_tool_calls(config):
    """Test _reconstruct_tool_calls merges streaming chunks."""
    runner = SessionRunner(config)

    # Simulate streaming tool call chunks - the function concatenates name and arguments
    chunk1 = {"index": 0, "id": "call_1", "function": {"name": "test_", "arguments": ""}}
    chunk2 = {"index": 0, "function": {"name": "tool", "arguments": '{"na'}}
    chunk3 = {"index": 0, "function": {"arguments": 'me": "test"}'}}
    tool_calls_data = [chunk1, chunk2, chunk3]

    result = runner._reconstruct_tool_calls(tool_calls_data)

    assert len(result) == 1
    assert result[0]["id"] == "call_1"
    assert result[0]["function"]["name"] == "test_tool"
    # Arguments are concatenated: "" + '{"na' + 'me": "test"}' = '{"name": "test"}'
    assert result[0]["function"]["arguments"] == '{"name": "test"}'


@pytest.mark.asyncio
async def test_reconstruct_tool_calls_multiple(config):
    """Test _reconstruct_tool_calls handles multiple tool calls."""
    runner = SessionRunner(config)

    tool_calls_data = [
        {"index": 0, "id": "call_1", "function": {"name": "tool1", "arguments": "{}"}},
        {"index": 1, "id": "call_2", "function": {"name": "tool2", "arguments": "{}"}},
    ]

    result = runner._reconstruct_tool_calls(tool_calls_data)

    assert len(result) == 2
    assert result[0]["function"]["name"] == "tool1"
    assert result[1]["function"]["name"] == "tool2"


def test_reconstruct_tool_calls_null_name(config):
    """Test _reconstruct_tool_calls handles null name in subsequent chunks."""
    runner = SessionRunner(config)

    # First chunk has name, subsequent chunks have name: null
    chunk1 = {"index": 0, "id": "call_1", "function": {"name": "bash", "arguments": ""}}
    chunk2 = {"index": 0, "function": {"name": None, "arguments": '{"com'}}
    chunk3 = {"index": 0, "function": {"arguments": 'mand"'}}  # no name field
    tool_calls_data = [chunk1, chunk2, chunk3]

    # Should not crash
    result = runner._reconstruct_tool_calls(tool_calls_data)

    assert len(result) == 1
    assert result[0]["function"]["name"] == "bash"
    assert result[0]["function"]["arguments"] == '{"command"'


def test_reconstruct_tool_calls_null_arguments(config):
    """Test _reconstruct_tool_calls handles null arguments in chunks."""
    runner = SessionRunner(config)

    # Chunks with null arguments
    chunk1 = {"index": 0, "id": "call_1", "function": {"name": "bash", "arguments": None}}
    chunk2 = {"index": 0, "function": {"arguments": '{"com'}}
    tool_calls_data = [chunk1, chunk2]

    # Should not crash
    result = runner._reconstruct_tool_calls(tool_calls_data)

    assert len(result) == 1
    assert result[0]["function"]["name"] == "bash"
    assert result[0]["function"]["arguments"] == '{"com'


class TestRunnerWorkspaceChanges:
    """Tests for workspace change handling."""

    @pytest.mark.asyncio
    async def test_handle_workspace_changes_tools(self, config):
        """Test handling tool changes."""
        runner = SessionRunner(config)
        async with runner:
            # Create a tool file
            tools_dir = config.tools_dir()
            tool_file = tools_dir / "new_tool.py"
            await tool_file.write_text("async def tool(x: int) -> int: return x")

            changes = ChangeSummary(
                tools_added=["new_tool"],
                tools_modified=[],
                tools_removed=[],
                skills_added=[],
                skills_modified=[],
                skills_removed=[],
                schedules_added=[],
                schedules_modified=[],
                schedules_removed=[],
            )

            await runner._handle_workspace_changes(changes)

            # Tool should be loaded
            assert "new_tool" in runner.registry.tools

    @pytest.mark.asyncio
    async def test_handle_workspace_changes_skills(self, config):
        """Test handling skill changes rebuilds system prompt."""
        runner = SessionRunner(config)
        async with runner:
            # Set up a mock system
            runner._system = MagicMock()
            runner._system.build_system_prompt = AsyncMock(return_value="New system prompt")

            changes = ChangeSummary(
                tools_added=[],
                tools_modified=[],
                tools_removed=[],
                skills_added=["skill1"],
                skills_modified=[],
                skills_removed=[],
                schedules_added=[],
                schedules_modified=[],
                schedules_removed=[],
            )

            await runner._handle_workspace_changes(changes)

            # System prompt should be rebuilt
            assert runner._system_prompt_cache == "New system prompt"


class TestRunnerStreaming:
    """Tests for streaming request handling."""

    @pytest.mark.asyncio
    async def test_process_streaming_request(self, config):
        """Test process_streaming_request returns stream generator."""
        runner = SessionRunner(config)
        async with runner:
            # Mock streaming response
            async def mock_stream():
                yield b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'
                yield b"data: [DONE]\n\n"

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = mock_stream()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                result = await runner.process_streaming_request({"role": "user", "content": "Hi"})

                # Result should be an async generator
                assert hasattr(result, "__aiter__")


class TestRunnerCompleteFn:
    """Tests for _complete_fn method."""

    @pytest.mark.asyncio
    async def test_complete_fn_success(self, config):
        """Test _complete_fn returns response content."""
        runner = SessionRunner(config)
        async with runner:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"choices": [{"message": {"content": "Summary text"}}]}
            )
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                result = await runner._complete_fn([{"role": "user", "content": "Summarize"}])

                assert result == "Summary text"

    @pytest.mark.asyncio
    async def test_complete_fn_error(self, config):
        """Test _complete_fn handles error response."""
        runner = SessionRunner(config)
        async with runner:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Error")
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                result = await runner._complete_fn([{"role": "user", "content": "Summarize"}])

                assert result == ""


class TestLoadSystem:
    """Tests for _load_system function."""

    @pytest.mark.asyncio
    async def test_load_system_with_system_class(self, tmp_path) -> None:
        workspace = anyio.Path(tmp_path)
        systems_dir = workspace / "systems"
        await systems_dir.mkdir()

        system_file = systems_dir / "system.py"
        await system_file.write_text(
            "class System:\n"
            "    def __init__(self, workspace):\n"
            "        self.workspace = workspace\n"
            "    async def build_system_prompt(self):\n"
            '        return "system prompt"\n'
            "    async def compact_history(self, history, complete_fn):\n"
            "        return history\n"
        )

        result = await _load_system(workspace)
        assert result is not None
        assert hasattr(result, "build_system_prompt")
        assert hasattr(result, "compact_history")
        prompt = await result.build_system_prompt()
        assert prompt == "system prompt"

    @pytest.mark.asyncio
    async def test_load_system_without_system_class(self, tmp_path) -> None:
        workspace = anyio.Path(tmp_path)
        systems_dir = workspace / "systems"
        await systems_dir.mkdir()

        system_file = systems_dir / "system.py"
        await system_file.write_text("x = 42\n")

        result = await _load_system(workspace)
        assert result is None

    @pytest.mark.asyncio
    async def test_load_system_no_file(self, tmp_path) -> None:
        workspace = anyio.Path(tmp_path)
        result = await _load_system(workspace)
        assert result is None


class TestHandleWorkspaceChangesScheduleBranches:
    """Tests for _handle_workspace_changes schedule branches."""

    @pytest.mark.asyncio
    async def test_schedules_added_triggers_add_schedule(self) -> None:
        runner = SessionRunner.__new__(SessionRunner)
        runner.config = MagicMock()
        runner.registry = MagicMock()
        runner._system = None
        runner._system_prompt_cache = None
        runner._schedule_executor = MagicMock()
        runner._schedule_executor.add_schedule = AsyncMock()
        runner._schedule_executor.update_schedule = AsyncMock()
        runner._schedule_executor.remove_schedule = AsyncMock()

        changes = ChangeSummary(
            tools_added=[],
            tools_modified=[],
            tools_removed=[],
            skills_added=[],
            skills_modified=[],
            skills_removed=[],
            schedules_added=["daily_summary"],
            schedules_modified=[],
            schedules_removed=[],
        )

        mock_schedule = MagicMock()
        with (
            patch("psi_agent.session.runner.load_schedule", return_value=mock_schedule),
            patch("psi_agent.session.runner.detect_and_update_tools", new_callable=AsyncMock),
        ):
            await runner._handle_workspace_changes(changes)

        runner._schedule_executor.add_schedule.assert_called_once_with(mock_schedule)

    @pytest.mark.asyncio
    async def test_schedules_modified_triggers_update_schedule(self) -> None:
        runner = SessionRunner.__new__(SessionRunner)
        runner.config = MagicMock()
        runner.registry = MagicMock()
        runner._system = None
        runner._system_prompt_cache = None
        runner._schedule_executor = MagicMock()
        runner._schedule_executor.add_schedule = AsyncMock()
        runner._schedule_executor.update_schedule = AsyncMock()
        runner._schedule_executor.remove_schedule = AsyncMock()

        changes = ChangeSummary(
            tools_added=[],
            tools_modified=[],
            tools_removed=[],
            skills_added=[],
            skills_modified=[],
            skills_removed=[],
            schedules_added=[],
            schedules_modified=["weekly_report"],
            schedules_removed=[],
        )

        mock_schedule = MagicMock()
        with (
            patch("psi_agent.session.runner.load_schedule", return_value=mock_schedule),
            patch("psi_agent.session.runner.detect_and_update_tools", new_callable=AsyncMock),
        ):
            await runner._handle_workspace_changes(changes)

        runner._schedule_executor.update_schedule.assert_called_once_with(mock_schedule)

    @pytest.mark.asyncio
    async def test_schedules_removed_triggers_remove_schedule(self) -> None:
        runner = SessionRunner.__new__(SessionRunner)
        runner.config = MagicMock()
        runner.registry = MagicMock()
        runner._system = None
        runner._system_prompt_cache = None
        runner._schedule_executor = MagicMock()
        runner._schedule_executor.add_schedule = AsyncMock()
        runner._schedule_executor.update_schedule = AsyncMock()
        runner._schedule_executor.remove_schedule = AsyncMock()

        changes = ChangeSummary(
            tools_added=[],
            tools_modified=[],
            tools_removed=[],
            skills_added=[],
            skills_modified=[],
            skills_removed=[],
            schedules_added=[],
            schedules_modified=[],
            schedules_removed=["old_task"],
        )

        with patch("psi_agent.session.runner.detect_and_update_tools", new_callable=AsyncMock):
            await runner._handle_workspace_changes(changes)

        runner._schedule_executor.remove_schedule.assert_called_once_with("old_task")


class TestBuildMessagesWithSystem:
    """Tests for _build_messages with System instance."""

    @pytest.mark.asyncio
    async def test_compact_history_called_when_system_available(self) -> None:
        from psi_agent.session.types import History

        runner = SessionRunner.__new__(SessionRunner)
        runner._system = MagicMock()
        runner._system.compact_history = AsyncMock(
            return_value=[{"role": "user", "content": "compacted"}]
        )
        runner.history = History(
            messages=[
                {"role": "user", "content": "old msg 1"},
                {"role": "user", "content": "old msg 2"},
            ]
        )
        runner._system_prompt_cache = "system prompt"
        runner._complete_fn = MagicMock()

        result = await runner._build_messages()

        runner._system.compact_history.assert_called_once()
        assert result[0] == {"role": "system", "content": "system prompt"}
        assert result[1] == {"role": "user", "content": "compacted"}

    @pytest.mark.asyncio
    async def test_compact_history_not_called_without_system(self) -> None:
        from psi_agent.session.types import History

        runner = SessionRunner.__new__(SessionRunner)
        runner._system = None
        runner.history = History(messages=[{"role": "user", "content": "hello"}])
        runner._system_prompt_cache = "system prompt"

        result = await runner._build_messages()

        assert result[0] == {"role": "system", "content": "system prompt"}
        assert result[1] == {"role": "user", "content": "hello"}


class TestReconstructToolCallsBoundary:
    """Boundary tests for _reconstruct_tool_calls."""

    def test_empty_list(self, config) -> None:
        runner = SessionRunner(config)
        result = runner._reconstruct_tool_calls([])
        assert result == []

    def test_non_contiguous_indices(self, config) -> None:
        chunks = [
            {"index": 0, "id": "call_1", "function": {"name": "read", "arguments": ""}},
            {"index": 3, "id": "call_2", "function": {"name": "write", "arguments": ""}},
        ]
        runner = SessionRunner(config)
        result = runner._reconstruct_tool_calls(chunks)
        assert len(result) == 2
        assert result[0]["function"]["name"] == "read"
        assert result[1]["function"]["name"] == "write"

    def test_function_name_as_none(self, config) -> None:
        chunks = [
            {"index": 0, "id": "call_1", "function": {"name": None, "arguments": ""}},
        ]
        runner = SessionRunner(config)
        result = runner._reconstruct_tool_calls(chunks)
        assert len(result) == 1
        assert result[0]["function"]["name"] == ""

    def test_multiple_tool_calls_interleaved(self, config) -> None:
        chunks = [
            {"index": 0, "id": "call_1", "function": {"name": "read", "arguments": ""}},
            {"index": 1, "id": "call_2", "function": {"name": "write", "arguments": ""}},
            {"index": 0, "function": {"arguments": "arg1"}},
            {"index": 1, "function": {"arguments": "arg2"}},
        ]
        runner = SessionRunner(config)
        result = runner._reconstruct_tool_calls(chunks)
        assert len(result) == 2
        assert result[0]["function"]["arguments"] == "arg1"
        assert result[1]["function"]["arguments"] == "arg2"


class TestFormatFunctionsEdgeCases:
    """Edge case tests for format functions."""

    def test_format_thinking_block_empty_string(self) -> None:
        result = format_thinking_block("")
        assert "<thinking>" in result
        assert "</thinking>" in result

    def test_format_tool_call_thinking_empty_result(self) -> None:
        result = format_tool_call_thinking(tool_name="test", arguments="{}", result="")
        assert isinstance(result, str)
        assert "<thinking>" in result
        assert isinstance(result, str)

    def test_format_thinking_block_with_xml_tags(self) -> None:
        content = "<tag>value</tag>"
        result = format_thinking_block(content)
        assert content in result


class TestRunnerScheduleExecutor:
    """Tests for schedule executor integration."""

    def test_set_schedule_executor(self, config):
        """Test setting schedule executor."""
        runner = SessionRunner(config)

        executor = MagicMock()
        runner.set_schedule_executor(executor)

        assert runner._schedule_executor == executor


@pytest.mark.asyncio
async def test_run_conversation_uses_streaming(config):
    """Test _run_conversation uses streaming internally for AI calls."""
    runner = SessionRunner(config)
    async with runner:
        # Create mock streaming response
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
            b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(runner.client, "post", return_value=mock_response) as mock_post:
            messages = [{"role": "user", "content": "Hi"}]
            result = await runner._run_conversation(messages)

            # Verify streaming was requested
            call_args = mock_post.call_args
            request_body = call_args[1]["json"]
            assert request_body.get("stream") is True

            # Verify response
            assert "choices" in result
            assert result["choices"][0]["message"]["content"] == "Hello world"


@pytest.mark.asyncio
async def test_run_conversation_handles_tool_calls_from_stream(config):
    """Test _run_conversation handles tool calls from streaming response."""
    runner = SessionRunner(config)
    async with runner:
        # Create a tool for testing
        tool_file = config.tools_dir() / "echo.py"
        await tool_file.write_text(
            """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
        )
        tool_schema = await load_tool_from_file(tool_file)
        if tool_schema:
            runner.registry.register(tool_schema)

        # First streaming response with tool call
        sse_lines_tool = [
            b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
            b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
            b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
            b'"function":{"arguments":"sage\\": \\"test\\"}"}}]}}\n',
            b"data: [DONE]\n",
        ]

        # Second streaming response after tool execution
        sse_lines_final = [
            b'data: {"choices":[{"delta":{"content":"Done"}}]}\n',
            b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
            b"data: [DONE]\n",
        ]

        call_count = 0

        def make_async_iter(lines):
            async def async_iter():
                for line in lines:
                    yield line

            return async_iter()

        def mock_post_side_effect(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            if call_count == 1:
                mock_response.content = make_async_iter(sse_lines_tool)
            else:
                mock_response.content = make_async_iter(sse_lines_final)

            return mock_response

        with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
            messages = [{"role": "user", "content": "Test tool"}]
            result = await runner._run_conversation(messages)

            # Should have made 2 calls (tool call + final response)
            assert call_count == 2
            assert "choices" in result
            # Check that thinking block is included
            content = result["choices"][0]["message"]["content"]
            assert "<thinking>" in content
            assert "[Tool: echo]" in content


def test_format_thinking_block():
    """Test format_thinking_block creates correct format."""
    content = "Test thinking"
    result = format_thinking_block(content)

    assert result == "<thinking>\nTest thinking\n</thinking>"


def test_format_tool_call_thinking():
    """Test format_tool_call_thinking creates correct format."""
    result = format_tool_call_thinking(
        tool_name="test_tool",
        arguments='{"arg": "value"}',
        result="success",
    )

    assert "<thinking>" in result
    assert "[Tool: test_tool]" in result
    assert 'Arguments: {"arg": "value"}' in result
    assert "Result: success" in result
    assert "</thinking>" in result


@pytest.mark.asyncio
async def test_run_conversation_includes_thinking(config):
    """Test _run_conversation includes thinking blocks for tool calls."""
    runner = SessionRunner(config)
    async with runner:
        # Create a tool for testing
        tool_file = config.tools_dir() / "echo.py"
        await tool_file.write_text(
            """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
        )
        tool_schema = await load_tool_from_file(tool_file)
        if tool_schema:
            runner.registry.register(tool_schema)

        # First streaming response with tool call
        sse_lines_tool = [
            b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
            b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
            b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
            b'"function":{"arguments":"sage\\": \\"test\\"}"}}]}}\n',
            b"data: [DONE]\n",
        ]

        # Second streaming response after tool execution
        sse_lines_final = [
            b'data: {"choices":[{"delta":{"content":"Done"}}]}\n',
            b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
            b"data: [DONE]\n",
        ]

        call_count = 0

        def make_async_iter(lines):
            async def async_iter():
                for line in lines:
                    yield line

            return async_iter()

        def mock_post_side_effect(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            if call_count == 1:
                mock_response.content = make_async_iter(sse_lines_tool)
            else:
                mock_response.content = make_async_iter(sse_lines_final)

            return mock_response

        with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
            messages = [{"role": "user", "content": "Test tool"}]
            result = await runner._run_conversation(messages)

            # Check that thinking block is prepended
            content = result["choices"][0]["message"]["content"]
            assert content.startswith("<thinking>")
            assert "[Tool: echo]" in content
            assert "Done" in content  # Final response is after thinking


class TestStreamConversation:
    """Tests for _stream_conversation method."""

    @pytest.mark.asyncio
    async def test_stream_conversation_yields_content(self, config):
        """Test _stream_conversation yields content chunks."""
        runner = SessionRunner(config)
        async with runner:
            sse_lines = [
                b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
                b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Hi"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should have content chunks and DONE
                assert len(chunks) > 0
                full_content = "".join(chunks)
                assert "Hello" in full_content or "world" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_handles_error(self, config):
        """Test _stream_conversation handles AI request failure."""
        runner = SessionRunner(config)
        async with runner:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Test"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should yield error content
                full_content = "".join(chunks)
                assert "Error" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_with_tool_calls(self, config):
        """Test _stream_conversation handles tool calls and yields thinking."""
        runner = SessionRunner(config)
        async with runner:
            # Create a tool
            tool_file = config.tools_dir() / "echo.py"
            await tool_file.write_text(
                """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
            )
            tool_schema = await load_tool_from_file(tool_file)
            if tool_schema:
                runner.registry.register(tool_schema)

            # First response with tool call
            sse_lines_tool = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
                b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"sage\\": \\"test\\"}"}}]}}\n',
                b"data: [DONE]\n",
            ]

            # Second response after tool execution
            sse_lines_final = [
                b'data: {"choices":[{"delta":{"content":"Done"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            call_count = 0

            def make_async_iter(lines):
                async def async_iter():
                    for line in lines:
                        yield line

                return async_iter()

            def mock_post_side_effect(*_args, **_kwargs):
                nonlocal call_count
                call_count += 1

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                if call_count == 1:
                    mock_response.content = make_async_iter(sse_lines_tool)
                else:
                    mock_response.content = make_async_iter(sse_lines_final)

                return mock_response

            with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
                messages = [{"role": "user", "content": "Test"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should include reasoning field with tool call info
                full_content = "".join(chunks)
                assert '"reasoning"' in full_content
                assert "[Tool: echo]" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_handles_null_tool_calls(self, config):
        """Test _stream_conversation handles null tool_calls value."""
        runner = SessionRunner(config)
        async with runner:
            # Response with null tool_calls (as observed from Tencent hy3 model)
            sse_lines = [
                b'data: {"choices":[{"delta":{"content":"","tool_calls":null}}]}\n',
                b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Hi"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should not crash and should yield content
                full_content = "".join(chunks)
                assert "Hello" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_handles_missing_tool_calls(self, config):
        """Test _stream_conversation handles missing tool_calls field."""
        runner = SessionRunner(config)
        async with runner:
            # Response without tool_calls field at all
            sse_lines = [
                b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Hi"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should not crash and should yield content
                full_content = "".join(chunks)
                assert "Hello" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_handles_valid_tool_calls(self, config):
        """Test _stream_conversation handles valid tool_calls array."""
        runner = SessionRunner(config)
        async with runner:
            # Create a tool
            tool_file = config.tools_dir() / "echo.py"
            await tool_file.write_text(
                """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
            )
            tool_schema = await load_tool_from_file(tool_file)
            if tool_schema:
                runner.registry.register(tool_schema)

            # Response with valid tool_calls array
            sse_lines_tool = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
                b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"sage\\": \\"test\\"}"}}]}}\n',
                b"data: [DONE]\n",
            ]

            sse_lines_final = [
                b'data: {"choices":[{"delta":{"content":"Done"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            call_count = 0

            def make_async_iter(lines):
                async def async_iter():
                    for line in lines:
                        yield line

                return async_iter()

            def mock_post_side_effect(*_args, **_kwargs):
                nonlocal call_count
                call_count += 1

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                if call_count == 1:
                    mock_response.content = make_async_iter(sse_lines_tool)
                else:
                    mock_response.content = make_async_iter(sse_lines_final)

                return mock_response

            with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
                messages = [{"role": "user", "content": "Test"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should process tool calls and include reasoning field
                full_content = "".join(chunks)
                assert '"reasoning"' in full_content
                assert "[Tool: echo]" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_handles_null_content(self, config):
        """Test _stream_conversation handles null content in delta."""
        runner = SessionRunner(config)
        async with runner:
            # Response with null content (as observed from Tencent hy3 model)
            # This happens when tool_calls are present but no text content
            sse_lines = [
                (
                    b'data: {"choices":[{"delta":{"content":null,"tool_calls":'
                    b'[{"index":0,"id":"call_1","function":{"name":"bash","arguments":""}}]}}]}\n'
                ),
                (
                    b'data: {"choices":[{"delta":{"content":null,"tool_calls":'
                    b'[{"index":0,"function":{"arguments":"{\\"com"}}]}}]}\n'
                ),
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Hi"}]
                chunks = []
                # This should not crash with TypeError
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should complete without error
                assert len(chunks) >= 0

    @pytest.mark.asyncio
    async def test_stream_conversation_handles_empty_string_content(self, config):
        """Test _stream_conversation handles empty string content in delta."""
        runner = SessionRunner(config)
        async with runner:
            # Response with empty string content
            sse_lines = [
                b'data: {"choices":[{"delta":{"content":""}}]}\n',
                b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Hi"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should not crash and should yield content
                full_content = "".join(chunks)
                assert "Hello" in full_content


class TestParseStreamingResponse:
    """Tests for _parse_streaming_response helper method."""

    @pytest.mark.asyncio
    async def test_parse_streaming_yields_content(self, config):
        """Test _parse_streaming_response yields content chunks."""
        runner = SessionRunner(config)

        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        assert len(results) == 2
        assert results[0][0] == "Hello"
        assert results[0][1] is None
        assert results[0][2] is None
        assert results[1][0] == " world"

    @pytest.mark.asyncio
    async def test_parse_streaming_yields_reasoning(self, config):
        """Test _parse_streaming_response yields reasoning chunks."""
        runner = SessionRunner(config)

        sse_lines = [
            b'data: {"choices":[{"delta":{"reasoning":"Thinking..."}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        assert len(results) == 1
        assert results[0][0] is None
        assert results[0][1] == "Thinking..."
        assert results[0][2] is None

    @pytest.mark.asyncio
    async def test_parse_streaming_yields_tool_calls(self, config):
        """Test _parse_streaming_response yields tool_calls chunks."""
        runner = SessionRunner(config)

        sse_lines = [
            (
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"id":"call_1","function":{"name":"bash","arguments":"{"}}]}}]}\n'
            ),
            (
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"}"}}]}}]}\n'
            ),
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        assert len(results) == 2
        assert results[0][2] is not None
        assert len(results[0][2]) == 1
        assert results[0][2][0]["function"]["name"] == "bash"

    @pytest.mark.asyncio
    async def test_parse_streaming_skips_empty_lines(self, config):
        """Test _parse_streaming_response skips empty lines and [DONE]."""
        runner = SessionRunner(config)

        sse_lines = [
            b"\n",  # Empty line
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"",  # Empty bytes
            b"data: [DONE]\n",
            b'data: {"choices":[{"delta":{"content":"After"}}]}\n',  # After DONE - still processed
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        # Empty lines and [DONE] marker are skipped, but content after [DONE] is still processed
        assert len(results) == 2
        assert results[0][0] == "Hello"
        assert results[1][0] == "After"

    @pytest.mark.asyncio
    async def test_parse_streaming_handles_invalid_json(self, config):
        """Test _parse_streaming_response handles invalid JSON gracefully."""
        runner = SessionRunner(config)

        sse_lines = [
            b"data: invalid json\n",
            b'data: {"choices":[{"delta":{"content":"Valid"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        # Invalid JSON should be skipped, valid JSON should be parsed
        assert len(results) == 1
        assert results[0][0] == "Valid"

    @pytest.mark.asyncio
    async def test_parse_streaming_handles_null_content(self, config):
        """Test _parse_streaming_response handles null content value."""
        runner = SessionRunner(config)

        sse_lines = [
            b'data: {"choices":[{"delta":{"content":null}}]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        assert len(results) == 2
        assert results[0][0] is None
        assert results[1][0] == "Hello"

    @pytest.mark.asyncio
    async def test_parse_streaming_handles_null_tool_calls(self, config):
        """Test _parse_streaming_response handles null tool_calls value."""
        runner = SessionRunner(config)

        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello","tool_calls":null}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        assert len(results) == 1
        assert results[0][0] == "Hello"
        assert results[0][2] is None

    @pytest.mark.asyncio
    async def test_parse_streaming_handles_all_fields(self, config):
        """Test _parse_streaming_response handles content, reasoning, and tool_calls together."""
        runner = SessionRunner(config)

        sse_lines = [
            (
                b'data: {"choices":[{"delta":{"content":"Hi","reasoning":"Think",'
                b'"tool_calls":[{"index":0,"id":"call_1","function":{"name":"bash","arguments":""}}]}}]}\n'
            ),
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        assert len(results) == 1
        assert results[0][0] == "Hi"
        assert results[0][1] == "Think"
        assert results[0][2] is not None
        assert len(results[0][2]) == 1

    @pytest.mark.asyncio
    async def test_parse_streaming_handles_missing_choices(self, config):
        """Test _parse_streaming_response handles missing choices array."""
        runner = SessionRunner(config)

        sse_lines = [
            b"data: {}\n",
            b'data: {"choices":[]}\n',
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b"data: [DONE]\n",
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        results = []
        async for content, reasoning, tool_calls in runner._parse_streaming_response(mock_response):
            results.append((content, reasoning, tool_calls))

        # Empty choices should yield None values
        assert len(results) == 3
        assert results[0][0] is None
        assert results[1][0] is None
        assert results[2][0] == "Hello"

    @pytest.mark.asyncio
    async def test_parse_streaming_raises_on_error_chunk(self, config):
        """Test _parse_streaming_response raises RuntimeError on error chunk."""
        runner = SessionRunner(config)

        sse_lines = [
            b'data: {"error": "Authentication failed", "status_code": 401}\n',
        ]

        async def async_iter():
            for line in sse_lines:
                yield line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = async_iter()

        with pytest.raises(RuntimeError, match="AI component error: Authentication failed"):
            async for _ in runner._parse_streaming_response(mock_response):
                pass


class TestRunConversationMultiRoundToolCalls:
    """Tests for _run_conversation with multiple rounds of tool calls (T10)."""

    @pytest.mark.asyncio
    async def test_two_rounds_of_tool_calls(self, config):
        """Test _run_conversation with two rounds of tool calls.

        LLM returns tool call, then after receiving tool result,
        returns another tool call, then finally returns text.
        """
        runner = SessionRunner(config)
        async with runner:
            # Create a tool
            tool_file = config.tools_dir() / "echo.py"
            await tool_file.write_text(
                """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
            )
            tool_schema = await load_tool_from_file(tool_file)
            if tool_schema:
                runner.registry.register(tool_schema)

            # First streaming response: tool call round 1
            sse_lines_round1 = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
                b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"sage\\": \\"hello\\"}"}}]}}\n',
                b"data: [DONE]\n",
            ]

            # Second streaming response: tool call round 2
            sse_lines_round2 = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_2",'
                b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"sage\\": \\"world\\"}"}}]}}\n',
                b"data: [DONE]\n",
            ]

            # Third streaming response: final text
            sse_lines_final = [
                b'data: {"choices":[{"delta":{"content":"All done"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            call_count = 0

            def make_async_iter(lines):
                async def async_iter():
                    for line in lines:
                        yield line

                return async_iter()

            def mock_post_side_effect(*_args, **_kwargs):
                nonlocal call_count
                call_count += 1

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                if call_count == 1:
                    mock_response.content = make_async_iter(sse_lines_round1)
                elif call_count == 2:
                    mock_response.content = make_async_iter(sse_lines_round2)
                else:
                    mock_response.content = make_async_iter(sse_lines_final)

                return mock_response

            with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
                messages = [{"role": "user", "content": "Test multi-round"}]
                result = await runner._run_conversation(messages)

                # Should have made 3 calls (2 tool call rounds + final response)
                assert call_count == 3
                assert "choices" in result
                content = result["choices"][0]["message"]["content"]
                # Both tool calls should have thinking blocks
                assert content.count("<thinking>") == 2
                assert "[Tool: echo]" in content
                assert "All done" in content

    @pytest.mark.asyncio
    async def test_tool_name_not_in_registry(self, config):
        """Test tool call with tool name not in registry returns error message.

        The conversation should continue after the error.
        """
        runner = SessionRunner(config)
        async with runner:
            # No tools registered - any tool call will fail

            # First streaming response: tool call with unknown tool
            sse_lines_tool = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
                b'"function":{"name":"nonexistent_tool","arguments":"{}"}}]}}]}\n',
                b"data: [DONE]\n",
            ]

            # Second streaming response: final text after error
            sse_lines_final = [
                b'data: {"choices":[{"delta":{"content":"I see the tool failed"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            call_count = 0

            def make_async_iter(lines):
                async def async_iter():
                    for line in lines:
                        yield line

                return async_iter()

            def mock_post_side_effect(*_args, **_kwargs):
                nonlocal call_count
                call_count += 1

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                if call_count == 1:
                    mock_response.content = make_async_iter(sse_lines_tool)
                else:
                    mock_response.content = make_async_iter(sse_lines_final)

                return mock_response

            with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
                messages = [{"role": "user", "content": "Test unknown tool"}]
                result = await runner._run_conversation(messages)

                # Should have made 2 calls (tool call + final response)
                assert call_count == 2
                assert "choices" in result
                content = result["choices"][0]["message"]["content"]
                # The thinking block should contain the error message
                assert "nonexistent_tool" in content
                # Conversation should have continued
                assert "I see the tool failed" in content

    @pytest.mark.asyncio
    async def test_tool_call_with_invalid_json_arguments(self, config):
        """Test tool call with invalid JSON arguments returns error message.

        The conversation should continue after the error.
        """
        runner = SessionRunner(config)
        async with runner:
            # Create a tool
            tool_file = config.tools_dir() / "echo.py"
            await tool_file.write_text(
                """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
            )
            tool_schema = await load_tool_from_file(tool_file)
            if tool_schema:
                runner.registry.register(tool_schema)

            # First streaming response: tool call with invalid JSON
            sse_lines_tool = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
                b'"function":{"name":"echo","arguments":"invalid json!!"}}]}}]}\n',
                b"data: [DONE]\n",
            ]

            # Second streaming response: final text
            sse_lines_final = [
                b'data: {"choices":[{"delta":{"content":"Continued after error"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            call_count = 0

            def make_async_iter(lines):
                async def async_iter():
                    for line in lines:
                        yield line

                return async_iter()

            def mock_post_side_effect(*_args, **_kwargs):
                nonlocal call_count
                call_count += 1

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                if call_count == 1:
                    mock_response.content = make_async_iter(sse_lines_tool)
                else:
                    mock_response.content = make_async_iter(sse_lines_final)

                return mock_response

            with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
                messages = [{"role": "user", "content": "Test invalid JSON"}]
                result = await runner._run_conversation(messages)

                # Should have made 2 calls (tool call + final response)
                assert call_count == 2
                assert "choices" in result
                content = result["choices"][0]["message"]["content"]
                # Conversation should have continued despite invalid JSON
                assert "Continued after error" in content


class TestRunnerWorkspaceChangeDetection:
    """Tests for workspace change handling with additional edge cases (T11)."""

    @pytest.mark.asyncio
    async def test_tools_removed_unregistered(self, config):
        """Test tools removed from workspace are unregistered from registry."""
        runner = SessionRunner(config)
        async with runner:
            # Create and register a tool
            tools_dir = config.tools_dir()
            tool_file = tools_dir / "temp_tool.py"
            await tool_file.write_text("async def tool(x: int) -> int: return x")
            tool_schema = await load_tool_from_file(tool_file)
            if tool_schema:
                runner.registry.register(tool_schema)
            assert "temp_tool" in runner.registry.tools

            # Now delete the tool file to simulate removal
            await tool_file.unlink()

            changes = ChangeSummary(
                tools_added=[],
                tools_modified=[],
                tools_removed=["temp_tool"],
                skills_added=[],
                skills_modified=[],
                skills_removed=[],
                schedules_added=[],
                schedules_modified=[],
                schedules_removed=[],
            )

            await runner._handle_workspace_changes(changes)

            # Tool should be unregistered
            assert "temp_tool" not in runner.registry.tools

    @pytest.mark.asyncio
    async def test_skills_changed_when_system_is_none(self, config):
        """Test skills changed when system is None sets cache to None."""
        runner = SessionRunner(config)
        async with runner:
            runner._system = None
            runner._system_prompt_cache = "old prompt"

            changes = ChangeSummary(
                tools_added=[],
                tools_modified=[],
                tools_removed=[],
                skills_added=["new_skill"],
                skills_modified=[],
                skills_removed=[],
                schedules_added=[],
                schedules_modified=[],
                schedules_removed=[],
            )

            await runner._handle_workspace_changes(changes)

            # System prompt cache should be set to None
            assert runner._system_prompt_cache is None

    @pytest.mark.asyncio
    async def test_schedules_changed_when_executor_is_none(self, config):
        """Test schedules changed when executor is None does not raise exception."""
        runner = SessionRunner(config)
        async with runner:
            runner._schedule_executor = None
            runner._system = None

            changes = ChangeSummary(
                tools_added=[],
                tools_modified=[],
                tools_removed=[],
                skills_added=[],
                skills_modified=[],
                skills_removed=[],
                schedules_added=["new_schedule"],
                schedules_modified=[],
                schedules_removed=[],
            )

            # Should not raise any exception
            await runner._handle_workspace_changes(changes)

    @pytest.mark.asyncio
    async def test_simultaneous_tools_skills_schedules_changes(self, config):
        """Test simultaneous tools, skills, and schedules changes are all applied."""
        runner = SessionRunner(config)
        async with runner:
            # Set up a mock system
            runner._system = MagicMock()
            runner._system.build_system_prompt = AsyncMock(return_value="Rebuilt prompt")

            # Set up a mock schedule executor
            runner._schedule_executor = MagicMock()
            runner._schedule_executor.add_schedule = AsyncMock()
            runner._schedule_executor.update_schedule = AsyncMock()
            runner._schedule_executor.remove_schedule = AsyncMock()

            # Create a tool file
            tools_dir = config.tools_dir()
            tool_file = tools_dir / "new_tool.py"
            await tool_file.write_text("async def tool(x: int) -> int: return x")

            changes = ChangeSummary(
                tools_added=["new_tool"],
                tools_modified=[],
                tools_removed=[],
                skills_added=["skill1"],
                skills_modified=[],
                skills_removed=[],
                schedules_added=["daily_task"],
                schedules_modified=[],
                schedules_removed=[],
            )

            mock_schedule = MagicMock()
            with (
                patch("psi_agent.session.runner.load_schedule", return_value=mock_schedule),
            ):
                await runner._handle_workspace_changes(changes)

            # Tool should be loaded
            assert "new_tool" in runner.registry.tools
            # System prompt should be rebuilt
            assert runner._system_prompt_cache == "Rebuilt prompt"
            # Schedule should be added
            runner._schedule_executor.add_schedule.assert_called_once_with(mock_schedule)


class TestCompleteFnAndStreaming:
    """Tests for _complete_fn and streaming edge cases (T12)."""

    @pytest.mark.asyncio
    async def test_complete_fn_with_none_content(self, config):
        """Test _complete_fn with None content returns empty string."""
        runner = SessionRunner(config)
        async with runner:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"choices": [{"message": {"content": None}}]}
            )
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                result = await runner._complete_fn([{"role": "user", "content": "Summarize"}])

                # message.get("content", "") returns None when key exists with None value
                assert result is None

    @pytest.mark.asyncio
    async def test_stream_conversation_with_reasoning_content(self, config):
        """Test _stream_conversation with reasoning content yields thinking block tags."""
        runner = SessionRunner(config)
        async with runner:
            sse_lines = [
                b'data: {"choices":[{"delta":{"reasoning":"Let me think..."}}]}\n',
                b'data: {"choices":[{"delta":{"reasoning":" Step 1 done."}}]}\n',
                b'data: {"choices":[{"delta":{"content":"Final answer"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Think about it"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                full_content = "".join(chunks)
                # Reasoning should be yielded as reasoning field
                assert '"reasoning"' in full_content
                assert "Let me think..." in full_content
                assert "Step 1 done." in full_content
                # Content should also be present
                assert "Final answer" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_with_both_reasoning_and_content(self, config):
        """Test _stream_conversation with both reasoning and content in same chunk."""
        runner = SessionRunner(config)
        async with runner:
            sse_lines = [
                b'data: {"choices":[{"delta":{"reasoning":"Thinking","content":"Speaking"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            async def async_iter():
                for line in sse_lines:
                    yield line

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content = async_iter()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            with patch.object(runner.client, "post", return_value=mock_response):
                messages = [{"role": "user", "content": "Hi"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                full_content = "".join(chunks)
                # Both reasoning and content should be present
                assert '"reasoning"' in full_content
                assert "Thinking" in full_content
                assert "Speaking" in full_content

    @pytest.mark.asyncio
    async def test_stream_conversation_multiple_rounds_of_tool_calls(self, config):
        """Test _stream_conversation with multiple rounds of tool calls."""
        runner = SessionRunner(config)
        async with runner:
            # Create a tool
            tool_file = config.tools_dir() / "echo.py"
            await tool_file.write_text(
                """
async def tool(message: str) -> str:
    '''Echo tool.

    Args:
        message: The message to echo.

    Returns:
        The echoed message.
    '''
    return message
"""
            )
            tool_schema = await load_tool_from_file(tool_file)
            if tool_schema:
                runner.registry.register(tool_schema)

            # Round 1: tool call
            sse_lines_round1 = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_1",'
                b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"sage\\": \\"first\\"}"}}]}}\n',
                b"data: [DONE]\n",
            ]

            # Round 2: another tool call
            sse_lines_round2 = [
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_2",'
                b'"function":{"name":"echo","arguments":"{\\"mes"}}]}}]}\n',
                b'data: {"choices":[{"delta":{"tool_calls":[{"index":0,'
                b'"function":{"arguments":"sage\\": \\"second\\"}"}}]}}\n',
                b"data: [DONE]\n",
            ]

            # Round 3: final text
            sse_lines_final = [
                b'data: {"choices":[{"delta":{"content":"Complete"}}]}\n',
                b'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n',
                b"data: [DONE]\n",
            ]

            call_count = 0

            def make_async_iter(lines):
                async def async_iter():
                    for line in lines:
                        yield line

                return async_iter()

            def mock_post_side_effect(*_args, **_kwargs):
                nonlocal call_count
                call_count += 1

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)

                if call_count == 1:
                    mock_response.content = make_async_iter(sse_lines_round1)
                elif call_count == 2:
                    mock_response.content = make_async_iter(sse_lines_round2)
                else:
                    mock_response.content = make_async_iter(sse_lines_final)

                return mock_response

            with patch.object(runner.client, "post", side_effect=mock_post_side_effect):
                messages = [{"role": "user", "content": "Test"}]
                chunks = []
                async for chunk in runner._stream_conversation(messages):
                    chunks.append(chunk)

                # Should have made 3 calls
                assert call_count == 3
                full_content = "".join(chunks)
                # Both tool calls should appear as reasoning
                assert full_content.count("[Tool: echo]") == 2
                assert "Complete" in full_content


class TestLoadSingleScheduleErrors:
    """Tests for _load_single_schedule error handling (T13)."""

    @pytest.mark.asyncio
    async def test_nonexistent_directory_returns_none(self, config):
        """Test _load_single_schedule with non-existent directory returns None."""
        runner = SessionRunner(config)
        result = await runner._load_single_schedule(anyio.Path("/nonexistent/path"))
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_task_md_returns_none(self, config):
        """Test _load_single_schedule with invalid TASK.md returns None."""
        runner = SessionRunner(config)
        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = anyio.Path(tmpdir) / "broken_task"
            await task_dir.mkdir()
            # Write TASK.md without required 'cron' field
            task_file = task_dir / "TASK.md"
            await task_file.write_text(
                "---\nname: broken\ndescription: No cron field\n---\nDo something\n"
            )

            result = await runner._load_single_schedule(task_dir)
            assert result is None
