"""Anthropic Messages API client for forwarding requests."""

import json
from collections.abc import AsyncGenerator
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types import Message
from loguru import logger

from psi_agent.ai.anthropic_messages.config import AnthropicMessagesConfig


class AnthropicMessagesClient:
    """Client for forwarding requests to Anthropic Messages API."""

    def __init__(self, config: AnthropicMessagesConfig) -> None:
        """Initialize the client.

        Args:
            config: The configuration for the client.
        """
        self.config = config
        self._client: AsyncAnthropic | None = None

    async def __aenter__(self) -> AnthropicMessagesClient:
        """Enter async context."""
        self._client = AsyncAnthropic(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        logger.debug(f"Initialized AsyncAnthropic client for {self.config.base_url}")
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit async context."""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.debug("Closed AsyncAnthropic client")

    async def messages(
        self, request_body: dict[str, Any], stream: bool = False
    ) -> dict[str, Any] | AsyncGenerator[str]:
        """Send messages request to Anthropic API.

        Args:
            request_body: The request body in Anthropic Messages format.
            stream: Whether to stream the response.

        Returns:
            For non-streaming: The response body as a dict.
            For streaming: An async generator of SSE chunks.
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # Inject model if not present
        if "model" not in request_body:
            request_body["model"] = self.config.model

        logger.info(f"Sending request to Anthropic API with model {request_body['model']}")
        logger.debug("Request headers: x-api-key=*** (hidden)")
        body_summary = {
            k: v if k != "messages" else f"[{len(v)} messages]" for k, v in request_body.items()
        }
        logger.debug(f"Request body summary: {body_summary}")

        if stream:
            return self._stream_request(request_body)
        else:
            return await self._non_stream_request(request_body)

    async def _non_stream_request(self, body: dict[str, Any]) -> dict[str, Any]:
        """Send non-streaming request.

        Args:
            body: The request body.

        Returns:
            The response body as a dict.
        """
        assert self._client is not None

        try:
            response: Message = await self._client.messages.create(**body)
            logger.info("Received successful non-streaming response")
            logger.debug(f"Response id: {response.id}")

            # Convert to dict for JSON serialization
            return response.model_dump()

        except Exception as e:
            return self._handle_error(e)

    async def _stream_request(self, body: dict[str, Any]) -> AsyncGenerator[str]:
        """Send streaming request.

        Args:
            body: The request body.

        Yields:
            SSE chunks as strings.
        """
        assert self._client is not None

        body["stream"] = True
        try:
            logger.info("Starting streaming request")
            async with self._client.messages.stream(**body) as stream:
                async for event in stream:
                    # Convert event to SSE format
                    event_data = event.model_dump()
                    yield f"event: {event.type}\ndata: {json.dumps(event_data)}\n\n"

            logger.info("Streaming response completed")
            yield "event: message_stop\ndata: {}\n\n"

        except Exception as e:
            error_response = self._handle_error(e)
            yield f"event: error\ndata: {json.dumps(error_response)}\n\n"

    def _handle_error(self, e: Exception) -> dict[str, Any]:
        """Handle API errors and return error response.

        Args:
            e: The exception that occurred.

        Returns:
            Error dict with status_code.
        """
        from anthropic import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            AuthenticationError,
            RateLimitError,
        )

        if isinstance(e, AuthenticationError):
            logger.error(f"Authentication failed: {e}")
            return {"error": "Authentication failed", "status_code": 401}

        if isinstance(e, RateLimitError):
            logger.error(f"Rate limit exceeded: {e}")
            return {"error": "Rate limit exceeded", "status_code": 429}

        if isinstance(e, APITimeoutError):
            logger.error(f"Request timeout: {e}")
            return {"error": "Request timeout", "status_code": 500}

        if isinstance(e, APIConnectionError):
            logger.error(f"Connection failed: {e}")
            return {"error": "Connection failed", "status_code": 500}

        if isinstance(e, APIStatusError):
            logger.error(f"API error {e.status_code}: {e}")
            return {"error": str(e), "status_code": e.status_code or 500}

        logger.exception(f"Unexpected error: {e}")
        return {"error": str(e), "status_code": 500}
