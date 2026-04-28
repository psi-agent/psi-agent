"""REPL interface for interactive conversation."""

from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from psi_agent.channel.repl.client import ReplClient
from psi_agent.channel.repl.config import ReplConfig


class Repl:
    """REPL interface for continuous conversation with psi-session."""

    def __init__(self, config: ReplConfig) -> None:
        """Initialize the REPL.

        Args:
            config: The configuration for the REPL.
        """
        self.config = config
        self.client = ReplClient(config)
        self.history: list[dict[str, str]] = []
        self._session: PromptSession[None] | None = None

    async def run(self) -> None:
        """Run the REPL loop."""
        print("psi-channel-repl - Interactive conversation with psi-session")
        print("Type /quit or press Ctrl+D to exit")
        print("Press Alt+Enter or Escape+Enter for new line\n")

        # Initialize prompt-toolkit session with history
        self._session = PromptSession(history=InMemoryHistory())

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

                    # Add user message to history
                    self.history.append({"role": "user", "content": user_input})

                    # Send to session and get response
                    response = await self.client.send_message(self.history)

                    # Display response
                    print(f"\n{response}\n")

                    # Add assistant response to history
                    self.history.append({"role": "assistant", "content": response})

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
            result = await self._session.prompt_async("> ", multiline=True)
            return result
        except EOFError:
            return None
