"""psi_agent.ai: LLM provider adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from tyro.conf import OmitSubcommandPrefixes

from psi_agent.ai.anthropic_messages.cli import AnthropicMessages
from psi_agent.ai.openai_completions import (
    OpenAICompletionsClient,
    OpenAICompletionsConfig,
    OpenAICompletionsServer,
)
from psi_agent.ai.openai_completions.cli import OpenaiCompletions

__all__ = [
    "OpenAICompletionsClient",
    "OpenAICompletionsServer",
    "OpenAICompletionsConfig",
    "Commands",
]


@dataclass
class Commands:
    """AI provider commands."""

    subcommand: Annotated[OpenaiCompletions | AnthropicMessages, OmitSubcommandPrefixes]

    def __call__(self) -> None:
        self.subcommand()
