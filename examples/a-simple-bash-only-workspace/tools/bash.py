"""Async bash tool for executing shell commands."""

import asyncio


async def tool(command: str, timeout: int = 30) -> str:
    """Execute a bash command asynchronously.

    Args:
        command: The bash command to execute.
        timeout: Timeout in seconds. Defaults to 30.

    Returns:
        Command output as string, or error message if execution fails.
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

        if process.returncode != 0:
            return f"Error (exit code {process.returncode}): {stderr.decode()}"
        return stdout.decode()
    except TimeoutError:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: {e}"
