"""HTTP server for Anthropic Messages over Unix socket."""

from __future__ import annotations

import json
from typing import Any

from aiohttp import web
from loguru import logger

from psi_agent.ai.anthropic_messages.client import AnthropicMessagesClient
from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig
from psi_agent.ai.anthropic_messages.translator import translate_openai_to_anthropic


class AnthropicMessagesServer:
    """HTTP server for Anthropic Messages over Unix socket."""

    def __init__(self, config: AnthropicMessagesConfig) -> None:
        """Initialize the server.

        Args:
            config: The configuration for the server.
        """
        self.config = config
        self.app = web.Application()
        self.client: AnthropicMessagesClient | None = None
        self._runner: web.AppRunner | None = None
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
            request: The incoming HTTP request.

        Returns:
            The HTTP response.
        """
        logger.info("Received POST /v1/chat/completions request")

        try:
            body = await request.json()
            logger.debug(f"Request body: {json.dumps(body, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse request body: {e}")
            return web.Response(status=400, text="Invalid JSON body")

        # Translate OpenAI format to Anthropic format
        anthropic_body = translate_openai_to_anthropic(body)

        stream = anthropic_body.get("stream", False)
        body_summary = {
            k: v if k != "messages" else f"[{len(v)} messages]" for k, v in anthropic_body.items()
        }
        logger.debug(f"Translated request body summary: {body_summary}")

        if self.client is None:
            logger.error("Client not initialized")
            return web.Response(status=500, text="Server not ready")

        try:
            if stream:
                logger.debug("Handling streaming request")
                return await self._handle_streaming(request, anthropic_body)
            else:
                logger.debug("Handling non-streaming request")
                return await self._handle_non_streaming(anthropic_body)
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            return web.Response(status=500, text=str(e))

    async def _handle_non_streaming(self, body: dict[str, Any]) -> web.Response:
        """Handle non-streaming request.

        Args:
            body: The request body.

        Returns:
            The HTTP response.
        """
        from collections.abc import AsyncGenerator

        assert self.client is not None
        result = await self.client.messages(body, stream=False)

        # Type narrowing: non-streaming returns dict, not AsyncGenerator
        assert not isinstance(result, AsyncGenerator)

        if "error" in result:
            status_code = result.get("status_code", 500)
            logger.error(f"Returning error response with status {status_code}")
            return web.Response(status=status_code, text=result["error"])

        logger.info("Returning successful non-streaming response")
        logger.debug(f"Response body: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return web.Response(status=200, body=json.dumps(result), content_type="application/json")

    async def _handle_streaming(
        self, request: web.Request, body: dict[str, Any]
    ) -> web.StreamResponse:
        """Handle streaming request.

        Args:
            request: The incoming HTTP request.
            body: The request body.

        Returns:
            The streaming HTTP response.
        """
        from collections.abc import AsyncGenerator
        from typing import cast

        assert self.client is not None

        response = web.StreamResponse()
        response.content_type = "text/event-stream"
        await response.prepare(request)

        logger.debug("Starting SSE stream")

        stream_result = await self.client.messages(body, stream=True)

        # Type narrowing: streaming returns AsyncGenerator[str]
        stream_gen = cast(AsyncGenerator[str], stream_result)

        async for chunk in stream_gen:
            await response.write(chunk.encode())

        logger.info("Streaming response completed")
        return response

    async def _handle_other(self, request: web.Request) -> web.Response:
        """Handle other requests.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response.
        """
        logger.warning(f"Received unhandled request: {request.method} {request.path}")
        return web.Response(status=404, text="Not found")

    async def start(self) -> None:
        """Start the server on Unix socket."""
        socket_path = self.config.socket_path()

        # Remove existing socket file if present
        if socket_path.exists():
            logger.debug(f"Removing existing socket file: {socket_path}")
            socket_path.unlink()

        # Initialize client
        self.client = AnthropicMessagesClient(self.config)
        assert self.client is not None
        await self.client.__aenter__()

        # Start server
        self._runner = web.AppRunner(self.app)
        await self._runner.setup()

        site = web.UnixSite(self._runner, str(socket_path))
        await site.start()

        logger.info(f"Server started on Unix socket: {socket_path}")
        logger.info(f"Model: {self.config.model}")
        logger.info(f"Base URL: {self.config.base_url}")

    async def stop(self) -> None:
        """Stop the server."""
        if self.client is not None:
            await self.client.__aexit__(None, None, None)
        if self._runner is not None:
            await self._runner.cleanup()
        logger.info("Server stopped")
