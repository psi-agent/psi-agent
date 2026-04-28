## Why

The codebase currently uses `pathlib.Path` for file system operations in several places, which performs synchronous (blocking) I/O that can block the async event loop. This violates the project's async interface specification which requires all I/O operations to use async methods. The CLAUDE.md explicitly states: "禁止使用 `pathlib.Path` 进行文件 IO 操作" (Forbidden to use `pathlib.Path` for file IO operations).

## What Changes

- Replace synchronous `pathlib.Path` operations with `anyio.Path` async equivalents in all source files
- Keep `pathlib.Path` for type annotations and path manipulation (no I/O operations)
- Update example workspace files to follow the same convention
- Fix the following files that have synchronous pathlib operations:

**Source files with issues:**
- `src/psi_agent/ai/anthropic_messages/server.py` - uses `Path.exists()` and `Path.unlink()` synchronously
- `src/psi_agent/ai/openai_completions/server.py` - already fixed (uses `anyio.Path`)
- `src/psi_agent/session/config.py` - uses `Path()` for return types (acceptable for type annotations)
- `src/psi_agent/session/runner.py` - uses `Path` for path manipulation only (acceptable)
- `src/psi_agent/session/schedule.py` - uses `Path` for type annotations and path manipulation (acceptable)
- `src/psi_agent/session/tool_loader.py` - uses `Path` for path manipulation only (acceptable)
- `src/psi_agent/session/workspace_watcher.py` - uses `Path` for path manipulation only (acceptable)

**Example files with issues:**
- `examples/a-simple-bash-only-workspace/systems/system.py` - uses `Path.exists()`, `Path.iterdir()`, `Path.read_text()` synchronously
- `examples/an-openclaw-like-workspace/systems/system.py` - uses `Path.exists()`, `Path.resolve()` synchronously

**Config files (acceptable usage):**
- Config files (`config.py`) that only use `Path()` for type conversion and return types are acceptable - no I/O operations performed

## Capabilities

### New Capabilities

- `async-file-operations`: Ensure all file system I/O operations use async methods via `anyio.Path` to prevent event loop blocking

### Modified Capabilities

None - this is an internal implementation improvement that doesn't change external behavior or APIs.

## Impact

- **Affected Code**: 
  - `src/psi_agent/ai/anthropic_messages/server.py` (2 synchronous operations)
  - `examples/a-simple-bash-only-workspace/systems/system.py` (multiple synchronous operations)
  - `examples/an-openclaw-like-workspace/systems/system.py` (multiple synchronous operations)

- **APIs**: No API changes - all changes are internal implementation details

- **Dependencies**: No new dependencies (`anyio` is already a dependency)

- **Systems**: No system-level changes required
