"""Tests for OpenAI completions configuration."""

from __future__ import annotations

import anyio

from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig


def test_config_creation() -> None:
    """Test basic config creation."""
    config = OpenAICompletionsConfig(
        session_socket="/tmp/test.sock",
        model="gpt-4",
        api_key="test-key",
        base_url="https://api.openai.com/v1",
    )

    assert config.session_socket == "/tmp/test.sock"
    assert config.model == "gpt-4"
    assert config.api_key == "test-key"
    assert config.base_url == "https://api.openai.com/v1"


def test_config_default_base_url() -> None:
    """Test default base_url."""
    config = OpenAICompletionsConfig(
        session_socket="/tmp/test.sock",
        model="gpt-4",
        api_key="test-key",
    )

    assert config.base_url == "https://api.openai.com/v1"


def test_socket_path() -> None:
    """Test socket_path method returns anyio.Path object."""
    config = OpenAICompletionsConfig(
        session_socket="/tmp/test.sock",
        model="gpt-4",
        api_key="test-key",
    )

    path = config.socket_path()
    assert isinstance(path, anyio.Path)
    assert path == anyio.Path("/tmp/test.sock")
