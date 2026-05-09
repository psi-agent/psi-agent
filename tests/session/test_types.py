"""Tests for session/types.py — ToolSchema, ToolRegistry, History."""

from __future__ import annotations

from psi_agent.session.types import History, ToolRegistry, ToolSchema


def _make_tool(name: str = "test_tool", file_hash: str = "abc123") -> ToolSchema:
    """Create a ToolSchema for testing."""

    async def tool_func() -> str:
        return "ok"

    return ToolSchema(
        name=name,
        schema={"type": "function", "function": {"name": name}},
        func=tool_func,
        file_hash=file_hash,
    )


class TestToolSchema:
    """Tests for ToolSchema construction."""

    def test_construction(self) -> None:
        tool = _make_tool("read", "hash1")
        assert tool.name == "read"
        assert tool.schema == {"type": "function", "function": {"name": "read"}}
        assert tool.file_hash == "hash1"
        assert callable(tool.func)

    def test_schema_dict_is_arbitrary(self) -> None:
        tool = ToolSchema(name="x", schema={"custom": True}, func=_make_tool().func, file_hash="h")
        assert tool.schema == {"custom": True}


class TestToolRegistryHappyPath:
    """Happy path tests for ToolRegistry."""

    def test_register_and_get(self) -> None:
        registry = ToolRegistry()
        tool = _make_tool("read")
        registry.register(tool)
        result = registry.get("read")
        assert result is tool

    def test_get_returns_none_for_missing(self) -> None:
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_unregister(self) -> None:
        registry = ToolRegistry()
        registry.register(_make_tool("read"))
        registry.unregister("read")
        assert registry.get("read") is None

    def test_list_tools_returns_schemas(self) -> None:
        registry = ToolRegistry()
        t1 = _make_tool("read")
        t2 = _make_tool("write")
        registry.register(t1)
        registry.register(t2)
        schemas = registry.list_tools()
        assert len(schemas) == 2
        assert t1.schema in schemas
        assert t2.schema in schemas

    def test_clear_empties_registry(self) -> None:
        registry = ToolRegistry()
        registry.register(_make_tool("read"))
        registry.register(_make_tool("write"))
        registry.clear()
        assert registry.get("read") is None
        assert registry.get("write") is None
        assert registry.list_tools() == []

    def test_register_multiple_tools(self) -> None:
        registry = ToolRegistry()
        for name in ("read", "write", "delete"):
            registry.register(_make_tool(name))
        assert len(registry.list_tools()) == 3
        for name in ("read", "write", "delete"):
            assert registry.get(name) is not None

    def test_default_empty_registry(self) -> None:
        registry = ToolRegistry()
        assert registry.tools == {}
        assert registry.list_tools() == []


class TestToolRegistryCornerCases:
    """Corner case tests for ToolRegistry."""

    def test_register_duplicate_overwrites(self) -> None:
        registry = ToolRegistry()
        registry.register(_make_tool("read", "hash1"))
        new_tool = _make_tool("read", "hash2")
        registry.register(new_tool)
        result = registry.get("read")
        assert result is new_tool
        assert result.file_hash == "hash2"

    def test_unregister_nonexistent_no_exception(self) -> None:
        registry = ToolRegistry()
        registry.unregister("nonexistent")  # should not raise

    def test_list_tools_empty_registry(self) -> None:
        registry = ToolRegistry()
        assert registry.list_tools() == []

    def test_get_nonexistent_returns_none(self) -> None:
        registry = ToolRegistry()
        registry.register(_make_tool("read"))
        assert registry.get("write") is None


class TestHistoryHappyPath:
    """Happy path tests for History."""

    def test_default_construction(self) -> None:
        history = History()
        assert history.messages == []
        assert history.history_file is None

    def test_construct_with_messages(self) -> None:
        msgs = [{"role": "user", "content": "hello"}]
        history = History(messages=msgs)
        assert len(history.messages) == 1
        assert history.messages[0]["content"] == "hello"

    def test_construct_with_history_file(self) -> None:
        history = History(history_file="/tmp/hist.json")
        assert history.history_file == "/tmp/hist.json"

    def test_add_message(self) -> None:
        history = History()
        history.add_message({"role": "user", "content": "hi"})
        assert len(history.messages) == 1
        assert history.messages[0] == {"role": "user", "content": "hi"}

    def test_clear(self) -> None:
        history = History()
        history.add_message({"role": "user", "content": "hi"})
        history.clear()
        assert history.messages == []


class TestHistoryCornerCases:
    """Corner case tests for History."""

    def test_add_message_various_roles(self) -> None:
        history = History()
        for role in ("user", "assistant", "system", "tool"):
            history.add_message({"role": role, "content": f"msg from {role}"})
        assert len(history.messages) == 4
        assert [m["role"] for m in history.messages] == ["user", "assistant", "system", "tool"]

    def test_messages_order_preserved(self) -> None:
        history = History()
        for i in range(10):
            history.add_message({"role": "user", "content": str(i)})
        assert [m["content"] for m in history.messages] == [str(i) for i in range(10)]

    def test_clear_then_add(self) -> None:
        history = History()
        history.add_message({"role": "user", "content": "old"})
        history.clear()
        history.add_message({"role": "user", "content": "new"})
        assert len(history.messages) == 1
        assert history.messages[0]["content"] == "new"

    def test_pre_populated_messages(self) -> None:
        msgs = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
        history = History(messages=msgs)
        assert len(history.messages) == 2
