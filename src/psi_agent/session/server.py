"""HTTP server for psi-session on Unix socket."""

import json
from typing import Any

from aiohttp import web
from loguru import logger

from psi_agent.session.config import SessionConfig
from psi_agent.session.runner import SessionRunner
from psi_agent.session.schedule import ScheduleExecutor, load_schedules


class SessionServer:
    """HTTP server for psi-session."""

    def __init__(self, config: SessionConfig) -> None:
        """Initialize server.

        Args:
            config: Session configuration.
        """
        self.config = config
        self.app = web.Application()
        self.runner: SessionRunner | None = None
        self._runner: web.AppRunner | None = None
        self._schedule_executor: ScheduleExecutor | None = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up HTTP routes."""
        self.app.router.add_post("/v1/chat/completions", self._handle_chat_completions)
        self.app.router.add_route("*", "/v1/{path:.*}", self._handle_other)
        logger.debug("Routes configured: POST /v1/chat/completions, wildcard /v1/*")

    async def _handle_chat_completions(
        self, request: web.Request
    ) -> web.Response | web.StreamResponse:
        """Handle chat completions request.

        Args:
            request: Incoming HTTP request.

        Returns:
            HTTP response.
        """
        logger.info("Received POST /v1/chat/completions request")

        if self.runner is None:
            logger.error("Runner not initialized")
            return web.Response(status=500, text="Server not ready")

        try:
            body = await request.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse request body: {e}")
            return web.Response(status=400, text="Invalid JSON body")

        stream = body.get("stream", False)
        messages = body.get("messages", [])

        if not messages:
            return web.Response(status=400, text="No messages provided")

        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg
                break

        if user_message is None:
            return web.Response(status=400, text="No user message found")

        logger.debug(f"Processing user message: {user_message.get('content', '')[:100]}...")

        try:
            if stream:
                logger.debug("Handling streaming request")
                return await self._handle_streaming(user_message)
            else:
                logger.debug("Handling non-streaming request")
                return await self._handle_non_streaming(user_message)
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            return web.Response(status=500, text=str(e))

    async def _handle_non_streaming(self, user_message: dict[str, Any]) -> web.Response:
        """Handle non-streaming request.

        Args:
            user_message: User message dict.

        Returns:
            HTTP response.
        """
        assert self.runner is not None

        result = await self.runner.process_request(user_message)

        # Extract only the final message for channel (hide tool calls)
        channel_response = self._filter_for_channel(result)

        logger.info("Returning successful non-streaming response")
        return web.Response(
            status=200,
            body=json.dumps(channel_response),
            content_type="application/json",
        )

    async def _handle_streaming(self, user_message: dict[str, Any]) -> web.StreamResponse:
        """Handle streaming request.

        Args:
            user_message: User message dict.

        Returns:
            Streaming HTTP response.
        """
        assert self.runner is not None

        response = web.StreamResponse()
        response.content_type = "text/event-stream"
        await response.prepare(request=web.Request)  # type: ignore

        logger.debug("Starting SSE stream")

        stream_gen = await self.runner.process_streaming_request(user_message)

        # Handle both async generator and dict response
        if hasattr(stream_gen, "__aiter__"):
            async for chunk in stream_gen:
                await response.write(chunk.encode())
        else:
            # Non-streaming result (tool calls were involved)
            result = stream_gen
            channel_response = self._filter_for_channel(result)
            data = json.dumps(channel_response)
            await response.write(f"data: {data}\n\n".encode())

        logger.info("Streaming response completed")
        return response

    def _filter_for_channel(self, result: dict[str, Any]) -> dict[str, Any]:
        """Filter response for channel, hiding tool calls and thinking.

        Args:
            result: Full LLM response.

        Returns:
            Filtered response for channel.
        """
        choices = result.get("choices", [])
        filtered_choices = []

        for choice in choices:
            message = choice.get("message", {})
            # Keep only role and content
            filtered_message = {
                "role": message.get("role", "assistant"),
                "content": message.get("content", ""),
            }
            filtered_choices.append(
                {
                    "message": filtered_message,
                    "finish_reason": choice.get("finish_reason", "stop"),
                }
            )

        return {
            "choices": filtered_choices,
            "model": result.get("model", "session"),
        }

    async def _handle_other(self, request: web.Request) -> web.Response:
        """Handle other requests.

        Args:
            request: Incoming HTTP request.

        Returns:
            HTTP response.
        """
        logger.warning(f"Received unhandled request: {request.method} {request.path}")
        return web.Response(status=404, text="Not found")

    async def start(self) -> None:
        """Start the server on Unix socket."""
        socket_path = self.config.channel_socket_path()

        # Remove existing socket file if present
        if socket_path.exists():
            logger.debug(f"Removing existing socket file: {socket_path}")
            socket_path.unlink()

        # Initialize runner
        self.runner = SessionRunner(self.config)
        await self.runner.__aenter__()

        # Load and start schedules
        schedules = await load_schedules(self.config.workspace_path())
        if schedules:
            self._schedule_executor = ScheduleExecutor(schedules, self.runner)
            await self._schedule_executor.start()

        # Start server
        self._runner = web.AppRunner(self.app)
        await self._runner.setup()

        site = web.UnixSite(self._runner, str(socket_path))
        await site.start()

        logger.info(f"Session server started on Unix socket: {socket_path}")
        logger.info(f"Workspace: {self.config.workspace}")
        if self.config.history_file:
            logger.info(f"History file: {self.config.history_file}")

    async def stop(self) -> None:
        """Stop the server."""
        # Stop schedule executor
        if self._schedule_executor is not None:
            await self._schedule_executor.stop()
            self._schedule_executor = None

        if self.runner is not None:
            await self.runner.__aexit__(None, None, None)
        if self._runner is not None:
            await self._runner.cleanup()
        logger.info("Session server stopped")
