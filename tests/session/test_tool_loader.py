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


class TestParseGoogleDocstringCornerCases:
    """Corner case tests for parse_google_docstring."""

    def test_only_returns_section(self) -> None:
        """Docstring with only Returns section (no Args)."""
        docstring = """Do something useful.

        Returns:
            A string result.
        """
        description, params = parse_google_docstring(docstring)
        assert "Do something useful" in description
        assert params == {}

    def test_only_args_section(self) -> None:
        """Docstring with only Args section (no Returns)."""
        docstring = """Do something.

        Args:
            x: The x parameter.
            y: The y parameter.
        """
        description, params = parse_google_docstring(docstring)
        assert "Do something" in description
        assert params["x"] == "The x parameter."
        assert params["y"] == "The y parameter."

    def test_nested_colons_in_param_descriptions(self) -> None:
        """Parameter descriptions containing colons."""
        docstring = """Do something.

        Args:
            url: The URL to connect to, e.g. http://example.com:8080.
            format: Output format: json or xml.
        """
        description, params = parse_google_docstring(docstring)
        assert "http://example.com:8080" in params["url"]
        assert "json or xml" in params["format"]

    def test_single_line_docstring(self) -> None:
        """Single-line docstring without Args or Returns."""
        docstring = "Just a simple description."
        description, params = parse_google_docstring(docstring)
        assert description == "Just a simple description."
        assert params == {}

    def test_unicode_content(self) -> None:
        """Docstring with Unicode characters."""
        docstring = """读取文件内容。

        Args:
            文件路径: 文件的路径。
        """
        description, params = parse_google_docstring(docstring)
        assert "读取文件内容" in description
        assert "文件的路径" in params["文件路径"]

    def test_args_with_no_space_after_colon(self) -> None:
        """Args where description starts immediately after colon."""
        docstring = """Do something.

        Args:
            x:First param description.
            y:Second param description.
        """
        description, params = parse_google_docstring(docstring)
        assert "First param" in params["x"]
        assert "Second param" in params["y"]


class TestPythonTypeToOpenaiTypeExtended:
    """Extended tests for python_type_to_openai_type."""

    def test_uppercase_list(self) -> None:
        """Test uppercase List type."""

        assert python_type_to_openai_type(list) == "array"

    def test_uppercase_dict(self) -> None:
        """Test uppercase Dict type."""

        assert python_type_to_openai_type(dict) == "object"

    def test_unknown_type_defaults_to_string(self) -> None:
        """Test that unknown types default to 'string'."""

        class CustomType:
            pass

        assert python_type_to_openai_type(CustomType) == "string"

    def test_all_standard_mappings(self) -> None:
        """Verify all standard type mappings."""
        mappings = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        for python_type, expected in mappings.items():
            assert python_type_to_openai_type(python_type) == expected


class TestGenerateToolSchemaBoundary:
    """Boundary tests for generate_tool_schema."""

    def test_function_with_no_parameters(self) -> None:
        """Function with no parameters at all."""

        async def no_params() -> str:
            """No params tool."""
            return "ok"

        schema = generate_tool_schema("no_params", no_params, "No params tool.", {})
        assert schema["function"]["parameters"]["properties"] == {}
        assert schema["function"]["parameters"]["required"] == []

    def test_function_with_all_defaults(self) -> None:
        """Function where all parameters have defaults."""

        async def all_defaults(x: int = 1, y: str = "a") -> str:
            """All defaults tool."""
            return "ok"

        schema = generate_tool_schema("all_defaults", all_defaults, "All defaults.", {})
        assert "x" in schema["function"]["parameters"]["properties"]
        assert "y" in schema["function"]["parameters"]["properties"]
        assert schema["function"]["parameters"]["required"] == []

    def test_mixed_required_optional(self) -> None:
        """Function with mixed required and optional parameters."""

        async def mixed(required_param: str, optional_param: int = 5) -> str:
            """Mixed params tool."""
            return "ok"

        schema = generate_tool_schema("mixed", mixed, "Mixed.", {})
        assert "required_param" in schema["function"]["parameters"]["required"]
        assert "optional_param" not in schema["function"]["parameters"]["required"]


class TestLoadToolFromFileExceptionPaths:
    """Exception path tests for load_tool_from_file."""

    @pytest.mark.asyncio
    async def test_empty_file(self) -> None:
        """Test loading an empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "empty.py"
            await tool_file.write_text("")
            result = await load_tool_from_file(tool_file)
            assert result is None

    @pytest.mark.asyncio
    async def test_file_with_only_comments(self) -> None:
        """Test loading a file with only comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "comments.py"
            await tool_file.write_text("# This is a comment\n# Another comment\n")
            result = await load_tool_from_file(tool_file)
            assert result is None

    @pytest.mark.asyncio
    async def test_tool_missing_type_annotations(self) -> None:
        """Test loading a tool function without type annotations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_file = anyio.Path(tmpdir) / "no_types.py"
            await tool_file.write_text("async def tool(x, y): return str(x + y)")
            result = await load_tool_from_file(tool_file)
            assert result is not None
            # Parameters without annotations should be skipped
            assert result.schema["function"]["parameters"]["properties"] == {}
