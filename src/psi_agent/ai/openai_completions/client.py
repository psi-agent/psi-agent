"""OpenAI API client for forwarding requests."""

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx
from loguru import logger

from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig


class OpenAICompletionsClient:
    """Client for forwarding requests to OpenAI-compatible APIs."""

    def __init__(self, config: OpenAICompletionsConfig) -> None:
        """Initialize the client.

        Args:
            config: The configuration for the client.
        """
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> OpenAICompletionsClient:
        """Enter async context."""
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0))
        logger.debug(f"Initialized httpx AsyncClient for {self.config.base_url}")
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit async context."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("Closed httpx AsyncClient")

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

        # Inject model if not present
        if "model" not in request_body:
            request_body["model"] = self.config.model

        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        logger.info(f"Sending request to {url}")
        logger.debug("Request headers: Authorization=Bearer *** (hidden)")
        body_summary = {
            k: v if k != "messages" else f"[{len(v)} messages]" for k, v in request_body.items()
        }
        logger.debug(f"Request body summary: {body_summary}")

        if stream:
            return self._stream_request(url, headers, request_body)
        else:
            return await self._non_stream_request(url, headers, request_body)

    async def _non_stream_request(
        self, url: str, headers: dict[str, str], body: dict[str, Any]
    ) -> dict[str, Any]:
        """Send non-streaming request.

        Args:
            url: The API URL.
            headers: The request headers.
            body: The request body.

        Returns:
            The response body as a dict.
        """
        assert self._client is not None

        try:
            response = await self._client.post(url, headers=headers, json=body)
            logger.debug(f"Response status: {response.status_code}")

            if response.status_code == 401:
                logger.error("API authentication failed (401)")
                return {"error": "Authentication failed", "status_code": 401}

            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}")
                return {"error": response.text, "status_code": response.status_code}

            result = response.json()
            logger.info("Received successful non-streaming response")
            logger.debug(f"Response keys: {list(result.keys())}")
            return result

        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to upstream API: {e}")
            return {"error": "Connection failed", "status_code": 500}
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            return {"error": "Request timeout", "status_code": 500}

    async def _stream_request(
        self, url: str, headers: dict[str, str], body: dict[str, Any]
    ) -> AsyncGenerator[str]:
        """Send streaming request.

        Args:
            url: The API URL.
            headers: The request headers.
            body: The request body.

        Yields:
            SSE chunks as strings.
        """
        assert self._client is not None

        body["stream"] = True
        try:
            async with self._client.stream("POST", url, headers=headers, json=body) as response:
                logger.debug(f"Stream response status: {response.status_code}")

                if response.status_code == 401:
                    logger.error("API authentication failed (401) during streaming")
                    error_data = {"error": "Authentication failed", "status_code": 401}
                    yield f"data: {json.dumps(error_data)}\n\n"
                    return

                if response.status_code != 200:
                    logger.error(f"Stream request failed with status {response.status_code}")
                    error_data = {"error": response.text, "status_code": response.status_code}
                    yield f"data: {json.dumps(error_data)}\n\n"
                    return

                logger.info("Started streaming response")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield line + "\n"
                    elif line == "":
                        yield "\n"

                logger.info("Streaming response completed")
                yield "data: [DONE]\n\n"

        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to upstream API during streaming: {e}")
            error_data = {"error": "Connection failed", "status_code": 500}
            yield f"data: {json.dumps(error_data)}\n\n"
        except httpx.TimeoutException as e:
            logger.error(f"Stream timeout: {e}")
            error_data = {"error": "Request timeout", "status_code": 500}
            yield f"data: {json.dumps(error_data)}\n\n"
