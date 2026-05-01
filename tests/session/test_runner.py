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
