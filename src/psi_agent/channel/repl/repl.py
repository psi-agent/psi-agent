"""REPL interface for interactive conversation."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from psi_agent.channel.repl.client import ReplClient
from psi_agent.channel.repl.config import ReplConfig


def _ensure_history_dir(history_path: Path) -> None:
    """Ensure the directory for the history file exists.

    Args:
        history_path: Path to the history file.
    """
    history_dir = history_path.parent
    if not history_dir.exists():
        history_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created history directory: {history_dir}")


class Repl:
    """REPL interface for continuous conversation with psi-session."""

    def __init__(self, config: ReplConfig) -> None:
        """Initialize the REPL.

        Args:
            config: The configuration for the REPL.
        """
        self.config = config
        self.client = ReplClient(config)
        self._session: PromptSession[None] | None = None

    async def run(self) -> None:
        """Run the REPL loop."""
        print("psi-channel-repl - Interactive conversation with psi-session")
        print("Type /quit or press Ctrl+D to exit")
        print("Press Alt+Enter or Escape+Enter for new line\n")

        # Initialize prompt-toolkit session with file-based history
        history_path = self.config.get_history_path()
        _ensure_history_dir(history_path)
        self._session = PromptSession(history=FileHistory(str(history_path)))

        async with self.client:
            while True:
                try:
                    # Read user input using prompt-toolkit async API
                    user_input = await self._read_input()
                    if user_input is None:
                        # EOF (Ctrl+D)
                        print("\nGoodbye!")
                        break

                    # Check for quit command
                    if user_input.strip().lower() == "/quit":
                        print("Goodbye!")
                        break

                    # Skip empty input
                    if not user_input.strip():
                        continue

                    # Send to session and get response
                    response = await self.client.send_message(user_input)

                    # Display response
                    print(f"\n{response}\n")

                except KeyboardInterrupt:
                    print("\n\nInterrupted. Type /quit or press Ctrl+D to exit.\n")
                    continue
                except Exception as e:
                    logger.exception(f"Unexpected error: {e}")
                    print(f"\nError: {e}\n")

    async def _read_input(self) -> str | None:
        """Read input from stdin asynchronously using prompt-toolkit.

        Returns:
            The input string, or None on EOF.
        """
        if self._session is None:
            return None

        try:
            # Use prompt-toolkit's async prompt with multiline support
            # Enter submits, Alt+Enter or Escape+Enter inserts newline
            # Continuation prompt (. ) for lines after the first
            result = await self._session.prompt_async(
                "> ", multiline=True, prompt_continuation=". "
            )
            return result
        except EOFError:
            return None
