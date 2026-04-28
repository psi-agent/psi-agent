## Context

The psi-agent project follows an async-first architecture where all I/O operations must use async methods to avoid blocking the event loop. The project uses `anyio` as the async I/O abstraction layer. However, some files still use synchronous `pathlib.Path` methods for file system operations, which violates this design principle.

**Current State:**
- `anyio` is already a project dependency
- Most files correctly use `anyio.Path` for async file operations
- A few files still use synchronous `pathlib.Path` methods

**Constraints:**
- Must maintain backward compatibility - no API changes
- `pathlib.Path` is acceptable for type annotations and pure path manipulation (no I/O)
- All actual file I/O must use `anyio.Path` async methods

## Goals / Non-Goals

**Goals:**
- Replace all synchronous `pathlib.Path` I/O operations with `anyio.Path` async equivalents
- Maintain consistent code style across the codebase
- Ensure the event loop is never blocked by file I/O

**Non-Goals:**
- Changing any external APIs or interfaces
- Refactoring unrelated code patterns
- Adding new features or capabilities

## Decisions

### Decision 1: Keep `pathlib.Path` for type annotations

**Rationale:** `pathlib.Path` is useful for type annotations and path manipulation that doesn't involve I/O. The `anyio.Path` class wraps `pathlib.Path` internally, so using `pathlib.Path` for annotations is semantically correct and avoids unnecessary conversions.

**Pattern:**
```python
# Acceptable - type annotation only
def get_path(self) -> Path:
    return Path(self.some_string)

# Acceptable - path manipulation without I/O
file_path = workspace / "tools" / "read.py"

# NOT acceptable - synchronous I/O
if file_path.exists():  # Blocks!
    content = file_path.read_text()  # Blocks!
```

### Decision 2: Use `anyio.Path` for all I/O operations

**Rationale:** `anyio.Path` provides async versions of all `pathlib.Path` I/O methods. The API is nearly identical, making migration straightforward.

**Migration mapping:**
| `pathlib.Path` (sync) | `anyio.Path` (async) |
|----------------------|---------------------|
| `path.exists()` | `await anyio.Path(path).exists()` |
| `path.is_file()` | `await anyio.Path(path).is_file()` |
| `path.is_dir()` | `await anyio.Path(path).is_dir()` |
| `path.read_text()` | `await anyio.Path(path).read_text()` |
| `path.read_bytes()` | `await anyio.Path(path).read_bytes()` |
| `path.write_text()` | `await anyio.Path(path).write_text()` |
| `path.unlink()` | `await anyio.Path(path).unlink()` |
| `path.mkdir()` | `await anyio.Path(path).mkdir()` |
| `path.rmdir()` | `await anyio.Path(path).rmdir()` |
| `path.iterdir()` | `async for p in anyio.Path(path).iterdir()` |
| `path.resolve()` | `await anyio.Path(path).resolve()` |

### Decision 3: Create `anyio.Path` instances inline

**Rationale:** Rather than storing `anyio.Path` instances, create them inline from strings or `pathlib.Path` objects when I/O is needed. This keeps the code simple and avoids confusion about when to use which type.

**Pattern:**
```python
# Good - create anyio.Path inline for I/O
if await anyio.Path(socket_path).exists():
    await anyio.Path(socket_path).unlink()

# Avoid - storing anyio.Path instances
self._path = anyio.Path(path)  # Can lead to confusion
```

## Risks / Trade-offs

### Risk: Mixed usage could cause confusion

**Mitigation:** Document the pattern clearly in CLAUDE.md (already done). The existing documentation clearly states when to use each type.

### Risk: Forgetting to await async operations

**Mitigation:** The `ty check` type checker will catch missing `await` statements. Additionally, `ruff` linting will flag async functions called without `await`.

### Risk: Performance overhead from creating `anyio.Path` instances

**Mitigation:** The overhead is negligible compared to actual I/O operations. `anyio.Path` is a thin wrapper around `pathlib.Path`.
