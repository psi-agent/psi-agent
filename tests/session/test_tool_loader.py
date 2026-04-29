"""Tests for tool_loader module."""

from __future__ import annotations

import tempfile

import anyio
import pytest

from psi_agent.session.tool_loader import (
    compute_file_hash,
    parse_google_docstring,
    python_type_to_openai_type,
    scan_tools_directory,
)


@pytest.mark.asyncio
async def test_compute_file_hash() -> None:
    """Test file hash computation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# test file\n")
        f.flush()
        hash1 = await compute_file_hash(anyio.Path(f.name))
        assert hash1 == await compute_file_hash(anyio.Path(f.name))  # Same content = same hash

        f.write("# modified\n")
        f.flush()
        hash2 = await compute_file_hash(anyio.Path(f.name))
        assert hash1 != hash2  # Different content = different hash


def test_parse_google_docstring() -> None:
    """Test Google docstring parsing."""
    docstring = """Read file content asynchronously.

    Args:
        file_path: Path to the file to read.
        encoding: File encoding to use.

    Returns:
        File content as string.
    """
    description, params = parse_google_docstring(docstring)
    assert description == "Read file content asynchronously."
    assert params["file_path"] == "Path to the file to read."
    assert params["encoding"] == "File encoding to use."


def test_parse_google_docstring_empty() -> None:
    """Test empty docstring parsing."""
    description, params = parse_google_docstring("")
    assert description == ""
    assert params == {}


def test_python_type_to_openai_type() -> None:
    """Test Python type to OpenAI type conversion."""
    assert python_type_to_openai_type(str) == "string"
    assert python_type_to_openai_type(int) == "integer"
    assert python_type_to_openai_type(float) == "number"
    assert python_type_to_openai_type(bool) == "boolean"
    assert python_type_to_openai_type(list) == "array"
    assert python_type_to_openai_type(dict) == "object"
    assert python_type_to_openai_type(None) == "string"


@pytest.mark.asyncio
async def test_scan_tools_directory() -> None:
    """Test tools directory scanning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tools_dir = anyio.Path(tmpdir)

        # Create some tool files
        await (tools_dir / "read.py").write_text("async def tool(file_path: str) -> str: pass")
        await (tools_dir / "write.py").write_text(
            "async def tool(file_path: str, content: str) -> str: pass"
        )
        await (tools_dir / "not_a_tool.txt").write_text("text file")

        result = await scan_tools_directory(tools_dir)

        assert len(result) == 2
        assert "read" in result
        assert "write" in result
        assert "not_a_tool" not in result


@pytest.mark.asyncio
async def test_scan_tools_directory_empty() -> None:
    """Test scanning empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await scan_tools_directory(anyio.Path(tmpdir))
        assert result == {}


@pytest.mark.asyncio
async def test_scan_tools_directory_nonexistent() -> None:
    """Test scanning nonexistent directory."""
    result = await scan_tools_directory(anyio.Path("/nonexistent/path"))
    assert result == {}
