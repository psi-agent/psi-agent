"""psi-channel-cli: Command-line channel for psi-agent."""

import asyncio
import sys

import aiohttp
import tyro
from loguru import logger


async def send_message(
    session_socket: str,
    message: str,
    stream: bool = False,
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
    import json

    content_parts = []

    async for line in response.content:
        line_str = line.decode().strip()
        if not line_str or line_str == "data: [DONE]":
            continue
        if line_str.startswith("data: "):
            try:
                chunk = json.loads(line_str[6:])
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                if "content" in delta:
                    content = delta["content"]
                    content_parts.append(content)
                    # Print chunk immediately for streaming
                    print(content, end="", flush=True)
            except json.JSONDecodeError:
                pass

    # Print newline after streaming completes
    print()
    return "".join(content_parts)


def run(
    session_socket: str,
    message: str,
    stream: bool = False,
) -> None:
    """Send a message to psi-session and print the response.

    Args:
        session_socket: Path to the session Unix socket.
        message: User message to send.
        stream: Whether to use streaming response.
    """
    logger.debug(f"Connecting to session socket: {session_socket}")
    logger.debug(f"Sending message: {message[:50]}...")

    result = asyncio.run(send_message(session_socket, message, stream))

    # For non-streaming, print the result
    # For streaming, it's already printed
    if not stream:
        print(result)

    # Exit with appropriate code
    if result.startswith("Error:"):
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(run)


if __name__ == "__main__":
    main()
