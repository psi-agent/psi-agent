## Context

The psi-agent framework follows an async-first design where all I/O operations should use async methods to avoid blocking the event loop. The project's CLAUDE.md explicitly states:

> **禁止使用 `pathlib.Path` 进行文件 IO 操作** — 所有文件操作方法（`read_text()`, `exists()`, `iterdir()` 等）都是同步的，会阻塞事件循环。必须使用 `anyio.Path` 的 async 方法。

Two example workspace files currently violate this guideline by using synchronous `pathlib.Path` methods for file I/O operations:

1. `examples/a-simple-bash-only-workspace/systems/system.py` - The `_parse_skill_description()` function uses `Path.read_text()` synchronously, and `build_system_prompt()` uses `Path.exists()`, `Path.iterdir()`, and `Path.is_dir()` synchronously.

2. `examples/an-openclaw-like-workspace/systems/system.py` - The `_read_bootstrap_file()` function uses `Path.exists()` synchronously.

## Goals / Non-Goals

**Goals:**
- Replace all synchronous `pathlib.Path` I/O operations with async `anyio.Path` equivalents
- Maintain functional equivalence - the code should behave identically after the change
- Follow the project's async coding standards as defined in CLAUDE.md

**Non-Goals:**
- Refactoring the overall structure of the system.py files
- Adding new features or changing the logic of the existing code
- Modifying test files (they already use appropriate async patterns where needed)

## Decisions

### Decision 1: Use `anyio.Path` for all file I/O

**Rationale:** `anyio.Path` provides an async-compatible wrapper around `pathlib.Path` that works with any async framework. This is the recommended approach in CLAUDE.md.

**Implementation pattern:**
```python
# Before (synchronous - blocking)
content = path.read_text()
if path.exists():
    ...
for item in path.iterdir():
    if item.is_dir():
        ...

# After (async - non-blocking)
content = await anyio.Path(path).read_text()
if await anyio.Path(path).exists():
    ...
async for item in anyio.Path(path).iterdir():
    if await anyio.Path(item).is_dir():
        ...
```

### Decision 2: Keep `pathlib.Path` for type annotations and path manipulation

**Rationale:** `pathlib.Path` can still be used for:
- Type annotations (e.g., `def __init__(self, workspace_dir: Path)`)
- Path manipulation without I/O (e.g., `workspace / "skills"`)
- Getting path properties like `.name`, `.stem`, `.suffix`

This is explicitly allowed by CLAUDE.md:
> `pathlib.Path` 可用于类型注解和路径拼接（无 IO 操作时）

## Risks / Trade-offs

**Risk: Breaking existing functionality** → Mitigation: The async operations are functionally equivalent to their sync counterparts. All existing tests should pass without modification.

**Risk: Missing some sync operations** → Mitigation: Careful code review to identify all sync operations. The grep pattern `pathlib.Path|from pathlib import` was used to find all relevant files.

**Trade-off: Slightly more verbose code** → The async versions require `await` and `async for`, but this is the correct pattern for async code and matches the rest of the codebase.
