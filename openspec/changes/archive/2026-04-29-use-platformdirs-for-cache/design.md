## Context

The codebase still has `pathlib.Path` imports in several locations:

1. **Source code**: `src/psi_agent/channel/repl/config.py` uses `pathlib.Path.home()` to construct the default history file path at `~/.cache/psi-agent/repl_history.txt`

2. **Examples**: Multiple files in `examples/` use `pathlib.Path` for file operations

3. **Tests**: Multiple test files use `pathlib.Path` for type annotations and path construction

The `platformdirs` library provides a unified API for determining platform-specific directories:
- **Linux**: `~/.cache/psi-agent/` (XDG Base Directory Specification)
- **macOS**: `~/Library/Caches/psi-agent/` (standard macOS cache location)
- **Windows**: `%LOCALAPPDATA%\psi-agent\` (Windows app data convention)

## Goals / Non-Goals

**Goals:**
- Replace manual path construction with `platformdirs.user_cache_dir()` for cache directory
- Replace all `pathlib.Path` imports in `examples/` with `anyio.Path`
- Replace all `pathlib.Path` imports in `tests/` with `anyio.Path` (keeping `SyncPath` alias only for pytest fixture type annotations)
- Ensure cross-platform compatibility for cache directory location

**Non-Goals:**
- Changing the history file name or structure
- Modifying any other configuration or behavior
- Migrating existing history files to new locations

## Decisions

### Use `platformdirs` library for cache directory

**Rationale**: `platformdirs` is a well-maintained, widely-used library that provides a simple API for determining platform-specific directories. It follows:
- XDG Base Directory Specification on Linux
- Apple's guidelines on macOS
- Microsoft's guidelines on Windows

### Use `anyio.Path` for all path operations

**Rationale**: All file operations should be async to avoid blocking the event loop. `anyio.Path` provides async methods for all file operations.

### Keep `SyncPath` alias for pytest fixtures

**Rationale**: pytest's `tmp_path` fixture returns `pathlib.Path`, not `anyio.Path`. We need to keep the `from pathlib import Path as SyncPath` import for type annotations on test fixtures, then convert to `anyio.Path` when using.

## Risks / Trade-offs

**Risk**: Existing users may have history files at `~/.cache/psi-agent/repl_history.txt` which won't be automatically migrated.

**Mitigation**: This is acceptable because:
1. The history file is non-critical (just convenience for REPL history)
2. Users can manually copy their history if needed
3. The new location is more correct according to platform conventions
