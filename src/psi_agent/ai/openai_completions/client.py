"""OpenAI API client for forwarding requests."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

from loguru import logger
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)
from openai.types.chat import ChatCompletion

from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig

# Known OpenAI SDK parameters for chat.completions.create()
# Provider-specific parameters (like 'thinking', 'reasoning_effort') are NOT included
# and will be passed via extra_body
KNOWN_SDK_PARAMS: set[str] = {
    "model",
    "messages",
    "temperature",
    "top_p",
    "n",
    "stream",
    "stop",
    "max_tokens",
    "presence_penalty",
    "frequency_penalty",
    "logit_bias",
    "user",
    "response_format",
    "tools",
    "tool_choice",
    "seed",
    "logprobs",
    "top_logprobs",
    "parallel_tool_calls",
    "stream_options",
    "service_tier",
    "modalities",
    "audio",
    "prediction",
    "metadata",
    "store",
}


class OpenAICompletionsClient:
    """Client for forwarding requests to OpenAI-compatible APIs."""

    def __init__(self, config: OpenAICompletionsConfig) -> None:
        """Initialize the client.

        Args:
            config: The configuration for the client.
        """
        self.config = config
        self._client: AsyncOpenAI | None = None

    def _split_params(self, body: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Split request body into SDK params and extra params.

        Args:
            body: The request body to split.

        Returns:
            A tuple of (sdk_params, extra_params). extra_params is None if empty.
        """
        sdk_params: dict[str, Any] = {}
        extra_params: dict[str, Any] = {}

        for key, value in body.items():
            if key in KNOWN_SDK_PARAMS:
                sdk_params[key] = value
            else:
                extra_params[key] = value

        return sdk_params, extra_params if extra_params else None

    async def __aenter__(self) -> OpenAICompletionsClient:
        """Enter async context."""
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        logger.debug(f"Initialized AsyncOpenAI client for {self.config.base_url}")
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit async context."""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.debug("Closed AsyncOpenAI client")

    async def chat_completions(
        self, request_body: dict[str, Any], stream: bool = False
    ) -> dict[str, Any] | AsyncGenerator[str]:
        """Send chat completions request to upstream API.

        Args:
            request_body: The request body in OpenAI chat completion format.
            stream: Whether to stream the response.

        Returns:
            For non-streaming: The response body as a dict.
            For streaming: An async generator of SSE chunks.
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        logger.info(f"Sending request to {self.config.base_url}/chat/completions")
        logger.debug("Request headers: Authorization=Bearer *** (hidden)")
        body_summary = {
            k: v if k != "messages" else f"[{len(v)} messages]" for k, v in request_body.items()
        }
        logger.debug(f"Request body summary: {body_summary}")
        logger.debug(f"Request body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")

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

        sdk_params, extra_params = self._split_params(body)

        try:
            response: ChatCompletion = await self._client.chat.completions.create(
                **sdk_params, extra_body=extra_params
            )
            logger.info("Received successful non-streaming response")
            logger.debug(f"Response id: {response.id}")
            logger.debug(
                f"Response body: {json.dumps(response.model_dump(), ensure_ascii=False, indent=2)}"
            )
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
        sdk_params, extra_params = self._split_params(body)

        try:
            logger.info("Starting streaming request")
            stream = await self._client.chat.completions.create(
                **sdk_params, extra_body=extra_params
            )
            async for chunk in stream:
                logger.debug(f"Stream chunk: {chunk.model_dump_json()}")
                yield f"data: {chunk.model_dump_json()}\n\n"

            logger.info("Streaming response completed")
            yield "data: [DONE]\n\n"

        except Exception as e:
            error_response = self._handle_error(e)
            yield f"data: {json.dumps(error_response)}\n\n"

    def _handle_error(self, e: Exception) -> dict[str, Any]:
        """Handle API errors and return error response.

        Args:
            e: The exception that occurred.

        Returns:
            Error dict with status_code.
        """
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
