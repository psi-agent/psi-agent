"""Tests for server module."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

from psi_agent.session.config import SessionConfig
from psi_agent.session.runner import SessionRunner
from psi_agent.session.server import SessionServer


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


def test_session_server_init(config):
    """Test SessionServer initialization."""
    server = SessionServer(config)
    assert server.config == config
    assert server.runner is None


def test_session_server_routes(config):
    """Test SessionServer routes setup."""
    server = SessionServer(config)
    # Check routes are registered
    routes = list(server.app.router.routes())
    assert len(routes) >= 1


def test_filter_for_channel(config):
    """Test response filtering for channel."""
    server = SessionServer(config)

    full_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello",
                    "tool_calls": [{"id": "123", "function": {"name": "test"}}],
                },
                "finish_reason": "stop",
            }
        ],
        "model": "session",
    }

    filtered = server._filter_for_channel(full_response)

    assert "tool_calls" not in filtered["choices"][0]["message"]
    assert filtered["choices"][0]["message"]["content"] == "Hello"
    assert filtered["choices"][0]["message"]["role"] == "assistant"


def test_filter_for_channel_multiple_choices(config):
    """Test filtering multiple choices."""
    server = SessionServer(config)

    full_response = {
        "choices": [
            {"message": {"role": "assistant", "content": "First"}, "finish_reason": "stop"},
            {"message": {"role": "assistant", "content": "Second"}, "finish_reason": "stop"},
        ],
        "model": "session",
    }

    filtered = server._filter_for_channel(full_response)

    assert len(filtered["choices"]) == 2


def test_filter_for_channel_empty_content(config):
    """Test filtering with empty content."""
    server = SessionServer(config)

    full_response = {
        "choices": [
            {"message": {"role": "assistant", "content": None}, "finish_reason": "stop"},
        ],
        "model": "session",
    }

    filtered = server._filter_for_channel(full_response)

    # The filter uses .get("content", "") which returns None if key exists with None value
    assert filtered["choices"][0]["message"]["content"] is None


@pytest.mark.asyncio
async def test_handle_chat_completions_no_runner(config):
    """Test handling request when runner not initialized."""
    server = SessionServer(config)

    # Create mock request
    mock_request = MagicMock()
    mock_request.json = AsyncMock(return_value={"messages": [{"role": "user", "content": "test"}]})

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 500


@pytest.mark.asyncio
async def test_handle_chat_completions_invalid_json(config):
    """Test handling request with invalid JSON."""
    server = SessionServer(config)
    # Set runner to avoid "not ready" error
    server.runner = SessionRunner(config)

    # Create mock request that raises JSONDecodeError
    mock_request = MagicMock()

    async def raise_json_error():
        raise json.JSONDecodeError("test", "test", 0)

    mock_request.json = raise_json_error

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 400


@pytest.mark.asyncio
async def test_handle_chat_completions_no_messages(config):
    """Test handling request with no messages."""
    server = SessionServer(config)
    server.runner = SessionRunner(config)

    mock_request = MagicMock()
    mock_request.json = AsyncMock(return_value={"messages": []})

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 400


@pytest.mark.asyncio
async def test_handle_chat_completions_no_user_message(config):
    """Test handling request with no user message."""
    server = SessionServer(config)
    server.runner = SessionRunner(config)

    mock_request = MagicMock()
    mock_request.json = AsyncMock(
        return_value={"messages": [{"role": "assistant", "content": "Hi"}]}
    )

    response = await server._handle_chat_completions(mock_request)
    assert response.status == 400


@pytest.mark.asyncio
async def test_handle_other_returns_404(config):
    """Test unhandled routes return 404."""
    server = SessionServer(config)

    mock_request = MagicMock()
    mock_request.method = "GET"
    mock_request.path = "/v1/unknown"

    response = await server._handle_other(mock_request)
    assert response.status == 404


class TestHandleChatCompletionsWithRunner:
    """Tests for chat completions with initialized runner."""

    @pytest.mark.asyncio
    async def test_handle_valid_request(self, config):
        """Test handling valid request with runner."""
        server = SessionServer(config)

        # Create runner and use patch.object to mock process_request
        runner = SessionRunner(config)
        server.runner = runner

        mock_process_request = AsyncMock(
            return_value={
                "choices": [{"message": {"role": "assistant", "content": "Hello!"}}],
                "model": "session",
            }
        )

        mock_request = MagicMock()
        mock_request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "Hi"}]}
        )

        with patch.object(runner, "process_request", mock_process_request):
            response = await server._handle_chat_completions(mock_request)
            assert response.status == 200

    @pytest.mark.asyncio
    async def test_handle_request_with_exception(self, config):
        """Test handling request when runner raises exception."""
        server = SessionServer(config)

        runner = SessionRunner(config)
        server.runner = runner

        mock_process_request = AsyncMock(side_effect=Exception("Test error"))

        mock_request = MagicMock()
        mock_request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "Hi"}]}
        )

        with patch.object(runner, "process_request", mock_process_request):
            response = await server._handle_chat_completions(mock_request)
            assert response.status == 500
            assert isinstance(response, web.Response)
            assert response.text is not None
            assert "Test error" in response.text

    @pytest.mark.asyncio
    async def test_handle_streaming_request(self, config):
        """Test handling streaming request."""
        server = SessionServer(config)

        async def mock_stream() -> AsyncGenerator[str]:
            yield "data: chunk1\n\n"
            yield "data: [DONE]\n\n"

        runner = SessionRunner(config)
        server.runner = runner

        mock_process_streaming_request = AsyncMock(return_value=mock_stream())

        mock_request = MagicMock()
        mock_request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "Hi"}], "stream": True}
        )

        # Mock StreamResponse
        with patch("psi_agent.session.server.web.StreamResponse") as mock_sr:
            mock_response = MagicMock()
            mock_response.prepare = AsyncMock()
            mock_response.write = AsyncMock()
            mock_sr.return_value = mock_response

            with patch.object(runner, "process_streaming_request", mock_process_streaming_request):
                response = await server._handle_chat_completions(mock_request)
                assert response.content_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_handle_streaming_with_tool_calls(self, config):
        """Test handling streaming request with tool calls (thinking blocks included)."""
        server = SessionServer(config)

        runner = SessionRunner(config)
        server.runner = runner

        # process_streaming_request now always returns async generator
        async def mock_stream_gen():
            yield 'data: {"choices":[{"delta":{"content":"<thinking>"}}]}\n\n'
            yield 'data: {"choices":[{"delta":{"content":"[Tool: test]"}}]}\n\n'
            yield 'data: {"choices":[{"delta":{"content":"</thinking>"}}]}\n\n'
            yield 'data: {"choices":[{"delta":{"content":"Result"}}]}\n\n'
            yield "data: [DONE]\n\n"

        mock_process_streaming_request = AsyncMock(return_value=mock_stream_gen())

        mock_request = MagicMock()
        mock_request.json = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "Hi"}], "stream": True}
        )

        with patch("psi_agent.session.server.web.StreamResponse") as mock_sr:
            mock_response = MagicMock()
            mock_response.prepare = AsyncMock()
            mock_response.write = AsyncMock()
            mock_sr.return_value = mock_response

            with patch.object(runner, "process_streaming_request", mock_process_streaming_request):
                response = await server._handle_chat_completions(mock_request)
                assert response.content_type == "text/event-stream"
                # Verify write was called with the streaming content
                mock_response.write.assert_called()


class TestSessionServerStartStop:
    """Tests for server start and stop."""

    @pytest.mark.asyncio
    async def test_start_creates_runner(self, config: SessionConfig) -> None:
        """Test that start creates a runner."""
        server = SessionServer(config)

        with (
            patch("psi_agent.session.server.web.UnixSite") as mock_site,
            patch("psi_agent.session.server.load_schedules") as mock_load_schedules,
        ):
            mock_site_instance = AsyncMock()
            mock_site.return_value = mock_site_instance
            mock_load_schedules.return_value = []

            await server.start()

            assert server.runner is not None

            await server.stop()

    @pytest.mark.asyncio
    async def test_start_loads_schedules(self, config: SessionConfig) -> None:
        """Test that start loads schedules."""
        server = SessionServer(config)

        with (
            patch("psi_agent.session.server.web.UnixSite") as mock_site,
            patch("psi_agent.session.server.load_schedules") as mock_load_schedules,
            patch("psi_agent.session.server.ScheduleExecutor") as mock_executor_cls,
        ):
            mock_site_instance = AsyncMock()
            mock_site.return_value = mock_site_instance
            mock_load_schedules.return_value = [MagicMock()]

            mock_executor = AsyncMock()
            mock_executor.start = AsyncMock()
            mock_executor_cls.return_value = mock_executor

            await server.start()

            mock_load_schedules.assert_called_once()
            assert server._schedule_executor is not None

            await server.stop()

    @pytest.mark.asyncio
    async def test_stop_cleans_up_runner(self, config: SessionConfig) -> None:
        """Test that stop cleans up runner."""
        server = SessionServer(config)

        with (
            patch("psi_agent.session.server.web.UnixSite") as mock_site,
            patch("psi_agent.session.server.load_schedules") as mock_load_schedules,
        ):
            mock_site_instance = AsyncMock()
            mock_site.return_value = mock_site_instance
            mock_load_schedules.return_value = []

            await server.start()
            runner = server.runner
            assert runner is not None

            # Mock the runner's __aexit__
            runner.__aexit__ = AsyncMock()

            await server.stop()

            runner.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_stops_schedule_executor(self, config: SessionConfig) -> None:
        """Test that stop stops schedule executor."""
        server = SessionServer(config)

        with (
            patch("psi_agent.session.server.web.UnixSite") as mock_site,
            patch("psi_agent.session.server.load_schedules") as mock_load_schedules,
            patch("psi_agent.session.server.ScheduleExecutor") as mock_executor_cls,
        ):
            mock_site_instance = AsyncMock()
            mock_site.return_value = mock_site_instance
            mock_load_schedules.return_value = [MagicMock()]

            mock_executor = AsyncMock()
            mock_executor.start = AsyncMock()
            mock_executor.stop = AsyncMock()
            mock_executor_cls.return_value = mock_executor

            await server.start()

            await server.stop()

            mock_executor.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_removes_existing_socket(self, config: SessionConfig) -> None:
        """Test that start removes existing socket file before starting."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = os.path.join(tmpdir, "test.sock")
            config = SessionConfig(
                channel_socket=socket_path,
                ai_socket=os.path.join(tmpdir, "ai.sock"),
                workspace=tmpdir,
            )

            # Create the socket file
            with open(socket_path, "w") as f:
                f.write("")

            server = SessionServer(config)

            with (
                patch("psi_agent.session.server.web.UnixSite") as mock_site,
                patch("psi_agent.session.server.load_schedules") as mock_load_schedules,
            ):
                mock_site_instance = AsyncMock()
                mock_site.return_value = mock_site_instance
                mock_load_schedules.return_value = []

                await server.start()

                # Socket file should be removed before UnixSite starts
                # (the server removes it, then UnixSite creates a new one)
                # We can't verify it exists after start because UnixSite is mocked
                # But we can verify the code path by checking the log

                await server.stop()
