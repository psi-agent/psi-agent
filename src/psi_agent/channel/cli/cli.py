"""psi-channel-cli: Command-line channel for psi-agent."""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass

import aiohttp
import tyro
from loguru import logger


async def send_message(
    session_socket: str,
    message: str,
    stream: bool = True,
) -> str:
    """Send a message to psi-session and return the response.

    Args:
        session_socket: Path to the session Unix socket.
        message: User message to send.
        stream: Whether to use streaming response.

    Returns:
        Agent response string.
    """
    connector = aiohttp.UnixConnector(path=session_socket)

    async with aiohttp.ClientSession(connector=connector) as client:
        # Build OpenAI chat completion request
        request_body = {
            "model": "session",
            "messages": [{"role": "user", "content": message}],
            "stream": stream,
        }
        logger.debug(f"Request body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")

        try:
            async with client.post(
                "http://localhost/v1/chat/completions",
                json=request_body,
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(f"Request failed: {response.status} - {text}")
                    return f"Error: {text}"

                if stream:
                    return await _handle_streaming(response)
                else:
                    return await _handle_non_streaming(response)

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection failed: {e}")
            return f"Error: Cannot connect to session socket at {session_socket}"


async def _handle_non_streaming(response: aiohttp.ClientResponse) -> str:
    """Handle non-streaming response.

    Args:
        response: HTTP response.

    Returns:
        Response content string.
    """
    result = await response.json()
    logger.debug(f"Response body: {json.dumps(result, ensure_ascii=False, indent=2)}")
    choices = result.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        return message.get("content", "")
    return ""


async def _handle_streaming(response: aiohttp.ClientResponse) -> str:
    """Handle streaming response.

    Args:
        response: HTTP response.

    Returns:
        Concatenated response content string.
    """
    content_parts = []

    async for line in response.content:
        line_str = line.decode().strip()
        if not line_str or line_str == "data: [DONE]":
            continue
        if line_str.startswith("data: "):
            try:
                chunk = json.loads(line_str[6:])
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content is not None:
                    content_parts.append(content)
                    truncated = content[:100]
                    suffix = "..." if len(content) > 100 else ""
                    logger.debug(f"Stream chunk: {truncated}{suffix}")
                    # Print chunk immediately for streaming
                    print(content, end="", flush=True)
            except json.JSONDecodeError:
                pass

    # Print newline after streaming completes
    print()
    return "".join(content_parts)


@dataclass
class Cli:
    """Send a message to psi-session."""

    session_socket: str
    message: str
    stream: bool = True
    """Enable streaming mode (default: streaming enabled)."""

    def __call__(self) -> None:
        logger.debug(f"Connecting to session socket: {self.session_socket}")
        logger.debug(f"Sending message: {self.message[:50]}...")

        result = asyncio.run(send_message(self.session_socket, self.message, self.stream))

        # For non-streaming, print the result
        # For streaming, it's already printed
        if not self.stream:
            print(result)

        # Exit with appropriate code
        if result.startswith("Error:"):
            sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(Cli)()


if __name__ == "__main__":
    main()
