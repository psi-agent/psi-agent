"""Tests for runner module."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import AsyncMock, patch

import anyio
import pytest

from psi_agent.session.config import SessionConfig
from psi_agent.session.runner import SessionRunner, load_system_prompt


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
        # Mock the AI client response using context manager
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "choices": [
                    {"message": {"role": "assistant", "content": "Hello!"}, "finish_reason": "stop"}
                ]
            }
        )
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
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Response text"},
                        "finish_reason": "stop",
                    }
                ]
            }
        )
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
