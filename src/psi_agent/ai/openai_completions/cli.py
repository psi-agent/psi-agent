"""CLI entry point for OpenAI completions server."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import tyro
from loguru import logger

from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig
from psi_agent.ai.openai_completions.server import OpenAICompletionsServer
from psi_agent.utils.proctitle import mask_sensitive_args


@dataclass
class OpenaiCompletions:
    """Run OpenAI completions server."""

    session_socket: str
    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    thinking: str | None = None
    reasoning_effort: str | None = None

    def __call__(self) -> None:
        # Mask sensitive arguments from process title
        mask_sensitive_args(["api_key"])

        config = OpenAICompletionsConfig(
            session_socket=self.session_socket,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            thinking=self.thinking,
            reasoning_effort=self.reasoning_effort,
        )

        logger.info("Starting psi-ai-openai-completions")
        logger.debug(
            f"Config: session_socket={self.session_socket}, "
            f"model={self.model}, base_url={self.base_url}"
        )

        server = OpenAICompletionsServer(config)

        async def _run() -> None:
            await server.start()
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
            finally:
                await server.stop()

        asyncio.run(_run())


def main() -> None:
    """Main entry point for CLI."""
    tyro.cli(OpenaiCompletions)()


if __name__ == "__main__":
    main()
