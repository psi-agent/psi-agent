## Context

The psi-agent codebase has a mix of `pathlib.Path` and `anyio.Path` usage. The project's coding standards explicitly require all IO operations to use async methods (`anyio.Path`) to avoid blocking the event loop. However, some files still use synchronous `pathlib.Path` methods for file operations.

### Current State

Files can be categorized into three patterns:

1. **Config files** - Return `pathlib.Path` for type annotations (no IO, acceptable)
2. **Files using `anyio.Path` for IO** - Already compliant
3. **Files with mixed usage** - Need migration to consistent async patterns

### Key Pattern

The problematic pattern is using `pathlib.Path` for operations that involve IO:
- `Path(file).exists()` → `await anyio.Path(file).exists()`
- `Path(file).read_text()` → `await anyio.Path(file).read_text()`
- `Path(dir).iterdir()` → `async for p in anyio.Path(dir).iterdir()`
- `Path(file).unlink()` → `await anyio.Path(file).unlink()`

## Goals / Non-Goals

**Goals:**
- Ensure all file IO operations use `anyio.Path` async methods
- Maintain consistent code style across the codebase
- Pass all lint, format, typing, and test checks

**Non-Goals:**
- Changing `pathlib.Path` usage for type annotations (no IO)
- Modifying any public API or behavior
- Adding new features or capabilities

## Decisions

### Decision 1: Keep `pathlib.Path` for type annotations and path manipulation

**Rationale:** `pathlib.Path` is appropriate for:
- Type annotations (e.g., `def foo(path: Path) -> None`)
- Path manipulation without IO (e.g., `path.parent`, `path / "subdir"`, `path.name`)
- Return types from config properties

**Alternative considered:** Use `anyio.Path` everywhere - rejected because it would require unnecessary awaits for non-IO operations.

### Decision 2: Use `anyio.Path` for all IO operations

**Rationale:** The `anyio.Path` class provides async versions of all `pathlib.Path` IO methods. This ensures non-blocking file operations in async contexts.

**Pattern:**
```python
# For IO operations
content = await anyio.Path(file_path).read_text()
exists = await anyio.Path(file_path).exists()
async for item in anyio.Path(dir_path).iterdir():
    ...

# For path manipulation (no IO)
parent = Path(file_path).parent
name = Path(file_path).name
```

### Decision 3: Handle hash computation functions

Several files compute file hashes using `Path(file_path)` passed to `compute_file_hash()`. The function reads file content, so it should use `anyio.Path` internally.

**Before:**
```python
file_hash = await compute_file_hash(Path(file_path))
```

**After:**
```python
file_hash = await compute_file_hash(anyio.Path(file_path))
# Or simply pass the anyio.Path directly if already available
```

## Risks / Trade-offs

### Risk: Inconsistent usage in complex functions
**Mitigation:** Review each file carefully, ensure all IO uses `anyio.Path`, keep `pathlib.Path` only for non-IO path manipulation.

### Risk: Missing some IO operations
**Mitigation:** Use `rg "Path\(" src` to find all `Path()` constructor calls and verify each one.

### Risk: Type checker complaints
**Mitigation:** Run `ty check` after each file migration to catch type issues early.
