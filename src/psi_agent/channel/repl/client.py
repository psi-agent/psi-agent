"""HTTP client for communicating with psi-session."""

from __future__ import annotations

import json
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

                message = choices[0].get("message", {})
                content = message.get("content", "")
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
