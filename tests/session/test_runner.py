"""Tests for runner module."""

import tempfile
from pathlib import Path

import pytest

from psi_agent.session.config import SessionConfig
from psi_agent.session.runner import SessionRunner, load_system_prompt


@pytest.fixture
def config():
    """Create test config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "tools").mkdir()

        yield SessionConfig(
            channel_socket=str(workspace / "channel.sock"),
            ai_socket=str(workspace / "ai.sock"),
            workspace=str(workspace),
            history_file=None,
        )


@pytest.mark.asyncio
async def test_load_system_prompt_no_file():
    """Test loading system prompt when no system.py exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await load_system_prompt(Path(tmpdir))
        assert result is None


@pytest.mark.asyncio
async def test_load_system_prompt_with_file():
    """Test loading system prompt from system.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        systems_dir = workspace / "systems"
        systems_dir.mkdir()

        system_file = systems_dir / "system.py"
        system_file.write_text(
            """
async def build_system_prompt() -> str:
    return "You are a helpful assistant."
"""
        )

        result = await load_system_prompt(workspace)
        assert result == "You are a helpful assistant."


@pytest.mark.asyncio
async def test_load_system_prompt_no_function():
    """Test loading system prompt when function doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        systems_dir = workspace / "systems"
        systems_dir.mkdir()

        system_file = systems_dir / "system.py"
        system_file.write_text("# no function here\n")

        result = await load_system_prompt(workspace)
        assert result is None


def test_session_runner_init(config):
    """Test SessionRunner initialization."""
    runner = SessionRunner(config)
    assert runner.config == config
    assert runner.registry is not None
    assert runner.history is None
    assert runner.client is None
