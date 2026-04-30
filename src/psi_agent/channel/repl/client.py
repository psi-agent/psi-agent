"""HTTP client for communicating with psi-session."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import aiohttp
from loguru import logger

from psi_agent.channel.repl.config import ReplConfig


class ReplClient:
    """Client for communicating with psi-session via Unix socket."""

    def __init__(self, config: ReplConfig) -> None:
        """Initialize the client.

        Args:
            config: The configuration for the client.
        """
        self.config = config
        self._session: aiohttp.ClientSession | None = None
        self._connector: aiohttp.UnixConnector | None = None

    async def __aenter__(self) -> ReplClient:
        """Enter async context."""
        socket_path = self.config.socket_path()
        self._connector = aiohttp.UnixConnector(path=str(socket_path))
        self._session = aiohttp.ClientSession(connector=self._connector)
        logger.debug(f"Initialized aiohttp session for Unix socket: {socket_path}")
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit async context."""
        if self._session is not None:
            await self._session.close()
            self._session = None
            logger.debug("Closed aiohttp session")
        if self._connector is not None:
            await self._connector.close()
            self._connector = None

    async def send_message_stream(
        self,
        message: str,
        on_chunk: Callable[[str], None] | None = None,
    ) -> str:
        """Send a message to psi-session with streaming response.

        Args:
            message: The user message string to send.
            on_chunk: Optional callback invoked for each content chunk.

        Returns:
            The complete assistant's response content.

        Raises:
            RuntimeError: If client is not initialized.
            aiohttp.ClientError: If request fails.
        """
        if self._session is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        body = {
            "messages": [{"role": "user", "content": message}],
            "stream": True,
        }
        logger.debug(f"Request body: {json.dumps(body, ensure_ascii=False, indent=2)}")

        logger.debug("Sending streaming message to session")

        try:
            async with self._session.post(url, headers=headers, json=body) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Session returned status {response.status}: {text}")
                    return f"Error: Session returned status {response.status}"

                # Parse SSE stream
                content_chunks = []
                async for line in response.content:
                    line_str = line.decode().strip()
                    if not line_str or line_str == "data: [DONE]":
                        continue
                    if line_str.startswith("data: "):
                        try:
                            chunk = json.loads(line_str[6:])
                            choices = chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    content_chunks.append(content)
                                    if on_chunk is not None:
                                        on_chunk(content)
                        except json.JSONDecodeError:
                            pass

                full_content = "".join(content_chunks)
                logger.debug(f"Received complete streaming response: {full_content[:100]}...")
                return full_content

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Failed to connect to session: {e}")
            return f"Error: Failed to connect to session at {self.config.session_socket}"
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return f"Error: Request failed - {e}"
        except TimeoutError:
            logger.error("Request timeout")
            return "Error: Request timeout"

    async def send_message(self, message: str) -> str:
        """Send a message to psi-session and return the response.

        Args:
            message: The user message string to send.

        Returns:
            The assistant's response content.

        Raises:
            RuntimeError: If client is not initialized.
            aiohttp.ClientError: If request fails.
        """
        if self._session is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = "http://localhost/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        body = {
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }
        logger.debug(f"Request body: {json.dumps(body, ensure_ascii=False, indent=2)}")

        logger.debug("Sending message to session")

        try:
            async with self._session.post(url, headers=headers, json=body) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Session returned status {response.status}: {text}")
                    return f"Error: Session returned status {response.status}"

                result = await response.json()
                logger.debug(f"Response body: {json.dumps(result, ensure_ascii=False, indent=2)}")
                choices = result.get("choices", [])
                if not choices:
                    logger.warning("Session returned no choices")
                    return "Error: No response from session"

                msg = choices[0].get("message", {})
                content = msg.get("content", "")
                logger.debug(f"Received response: {content[:100]}...")
                return content

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Failed to connect to session: {e}")
            return f"Error: Failed to connect to session at {self.config.session_socket}"
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return f"Error: Request failed - {e}"
        except TimeoutError:
            logger.error("Request timeout")
            return "Error: Request timeout"
