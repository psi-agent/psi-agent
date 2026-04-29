"""Tests for tool_loader module."""

from __future__ import annotations

import tempfile

import anyio
import pytest

from psi_agent.session.tool_loader import (
    compute_file_hash,
    detect_and_update_tools,
    generate_tool_schema,
    load_all_tools,
    load_tool_from_file,
    parse_google_docstring,
    python_type_to_openai_type,
    scan_tools_directory,
)
from psi_agent.session.types import ToolRegistry


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


class TestLoadToolFromFile:
    """Tests for load_tool_from_file function."""

    @pytest.mark.asyncio
    async def test_load_valid_tool(self) -> None:
        """Test loading a valid tool file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "test_tool.py"
            await tool_file.write_text(
                '''
async def tool(file_path: str) -> str:
    """Read file content.

    Args:
        file_path: Path to the file.

    Returns:
        File content.
    """
    return "content"
'''
            )

            result = await load_tool_from_file(tool_file)

            assert result is not None
            assert result.name == "test_tool"
            assert "test_tool" in result.schema["function"]["name"]

    @pytest.mark.asyncio
    async def test_load_tool_no_tool_function(self) -> None:
        """Test loading a file without tool function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "no_tool.py"
            await tool_file.write_text("def other_func(): pass")

            result = await load_tool_from_file(tool_file)

            assert result is None

    @pytest.mark.asyncio
    async def test_load_tool_not_async(self) -> None:
        """Test loading a file with non-async tool function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "sync_tool.py"
            await tool_file.write_text("def tool(file_path: str) -> str: return 'content'")

            result = await load_tool_from_file(tool_file)

            assert result is None

    @pytest.mark.asyncio
    async def test_load_tool_with_syntax_error(self) -> None:
        """Test loading a file with syntax error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "bad_syntax.py"
            await tool_file.write_text("def tool(: pass")  # Invalid syntax

            result = await load_tool_from_file(tool_file)

            assert result is None

    @pytest.mark.asyncio
    async def test_load_tool_with_import_error(self) -> None:
        """Test loading a file with import error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "import_error.py"
            await tool_file.write_text("import nonexistent_module\nasync def tool(): pass")

            result = await load_tool_from_file(tool_file)

            assert result is None


class TestGenerateToolSchema:
    """Tests for generate_tool_schema function."""

    async def dummy_tool(self, name: str, count: int = 10) -> str:
        """A dummy tool for testing.

        Args:
            name: The name parameter.
            count: The count parameter.

        Returns:
            A result string.
        """
        return "result"

    def test_generate_schema_with_defaults(self) -> None:
        """Test schema generation with default parameters."""
        schema = generate_tool_schema(
            "dummy",
            self.dummy_tool,
            "A dummy tool for testing.",
            {"name": "The name parameter.", "count": "The count parameter."},
        )

        assert schema["type"] == "function"
        assert schema["function"]["name"] == "dummy"
        assert schema["function"]["description"] == "A dummy tool for testing."
        assert "name" in schema["function"]["parameters"]["properties"]
        assert "count" in schema["function"]["parameters"]["properties"]
        assert "name" in schema["function"]["parameters"]["required"]
        assert "count" not in schema["function"]["parameters"]["required"]

    def test_generate_schema_no_annotation(self) -> None:
        """Test schema generation skips parameters without annotation."""

        async def tool_no_annotation(name, count: int = 5) -> str:
            """Tool without full annotations."""
            return "result"

        schema = generate_tool_schema(
            "no_annot",
            tool_no_annotation,
            "Tool description.",
            {},
        )

        # Only 'count' should be in properties (has annotation)
        assert "count" in schema["function"]["parameters"]["properties"]
        assert "name" not in schema["function"]["parameters"]["properties"]


class TestLoadAllTools:
    """Tests for load_all_tools function."""

    @pytest.mark.asyncio
    async def test_load_all_tools(self) -> None:
        """Test loading all tools from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_dir = anyio.Path(tmpdir)

            await (tools_dir / "tool1.py").write_text("async def tool(x: int) -> int: return x")
            await (tools_dir / "tool2.py").write_text("async def tool(y: str) -> str: return y")

            registry = ToolRegistry()
            await load_all_tools(tools_dir, registry)

            assert "tool1" in registry.tools
            assert "tool2" in registry.tools

    @pytest.mark.asyncio
    async def test_load_all_tools_empty_dir(self) -> None:
        """Test loading from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ToolRegistry()
            await load_all_tools(anyio.Path(tmpdir), registry)

            assert len(registry.tools) == 0


class TestDetectAndUpdateTools:
    """Tests for detect_and_update_tools function."""

    @pytest.mark.asyncio
    async def test_detect_new_tools(self) -> None:
        """Test detecting and adding new tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_dir = anyio.Path(tmpdir)
            await (tools_dir / "new_tool.py").write_text("async def tool(x: int) -> int: return x")

            registry = ToolRegistry()
            await detect_and_update_tools(tools_dir, registry)

            assert "new_tool" in registry.tools

    @pytest.mark.asyncio
    async def test_detect_removed_tools(self) -> None:
        """Test detecting and removing tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_dir = anyio.Path(tmpdir)

            # Create initial tool
            tool_file = tools_dir / "old_tool.py"
            await tool_file.write_text("async def tool(x: int) -> int: return x")

            registry = ToolRegistry()
            await load_all_tools(tools_dir, registry)
            assert "old_tool" in registry.tools

            # Remove the tool file
            await tool_file.unlink()

            # Update should remove the tool
            await detect_and_update_tools(tools_dir, registry)
            assert "old_tool" not in registry.tools

    @pytest.mark.asyncio
    async def test_detect_updated_tools(self) -> None:
        """Test detecting and updating changed tools."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_dir = anyio.Path(tmpdir)
            tool_file = tools_dir / "changed_tool.py"

            # Create initial tool
            await tool_file.write_text(
                '''async def tool(x: int) -> int:
    """Version 1."""
    return x
'''
            )

            registry = ToolRegistry()
            await load_all_tools(tools_dir, registry)
            original_hash = registry.tools["changed_tool"].file_hash

            # Modify the tool
            await tool_file.write_text(
                '''async def tool(x: int) -> int:
    """Version 2."""
    return x * 2
'''
            )

            await detect_and_update_tools(tools_dir, registry)
            new_hash = registry.tools["changed_tool"].file_hash

            assert original_hash != new_hash


class TestParseGoogleDocstring:
    """Additional tests for parse_google_docstring."""

    def test_multiline_param_description(self) -> None:
        """Test parsing multiline parameter descriptions."""
        docstring = """Do something.

        Args:
            param1: First line of description.
                Second line of description.
                Third line.

        Returns:
            Result.
        """
        description, params = parse_google_docstring(docstring)
        assert "First line" in params["param1"]
        assert "Second line" in params["param1"]
        assert "Third line" in params["param1"]

    def test_no_args_section(self) -> None:
        """Test parsing docstring without Args section.

        Note: The function only extracts Args section, so Returns and other
        sections are included in the description.
        """
        docstring = """Just a description.

        Returns:
            Something.
        """
        description, params = parse_google_docstring(docstring)
        # The description includes everything since there's no Args: marker
        assert "Just a description" in description
        assert params == {}
