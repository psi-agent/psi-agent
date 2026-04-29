## Why

The codebase currently has mixed usage of `pathlib.Path` and `anyio.Path` for file operations. According to the project's async interface specification, all IO operations must use async methods to avoid blocking the event loop. Some files still use `pathlib.Path` for IO operations (like `read_text()`, `exists()`, `iterdir()`) which are synchronous and block the event loop.

## What Changes

- Replace `pathlib.Path` IO operations with `anyio.Path` async equivalents across all source files
- Keep `pathlib.Path` for type annotations and path manipulation (no IO) where appropriate
- Ensure all file system operations use async patterns consistently

### Files requiring migration:

1. **Config files** (return `Path` for type annotations - OK, but need review):
   - `src/psi_agent/channel/telegram/config.py`
   - `src/psi_agent/channel/repl/config.py`
   - `src/psi_agent/session/config.py`
   - `src/psi_agent/ai/anthropic_messages/config.py`
   - `src/psi_agent/ai/openai_completions/config.py`

2. **Files with mixed usage** (need careful migration):
   - `src/psi_agent/session/schedule.py` - uses `Path(entry)` for hash computation
   - `src/psi_agent/session/workspace_watcher.py` - uses `Path(file_path)` for hash computation
   - `src/psi_agent/session/tool_loader.py` - uses `Path(file_path)` for hash computation
   - `src/psi_agent/workspace/snapshot/api.py` - uses `Path()` for path resolution and `Path()` in `_copy_directory`
   - `src/psi_agent/workspace/umount/api.py` - uses `Path()` for path resolution
   - `src/psi_agent/workspace/mount/api.py` - uses `Path()` for path resolution
   - `src/psi_agent/workspace/unpack/api.py` - uses `Path()` for path resolution
   - `src/psi_agent/workspace/pack/api.py` - uses `Path()` for path resolution
   - `src/psi_agent/ai/openai_completions/server.py` - uses `Path()` for socket path

## Capabilities

### New Capabilities

None - this is an internal refactoring to improve async consistency.

### Modified Capabilities

None - no spec-level behavior changes, only implementation details.

## Impact

- **Affected files**: All files in `src/psi_agent/` that use `pathlib.Path` for IO operations
- **No API changes**: All public interfaces remain the same
- **No breaking changes**: Internal implementation only
- **Testing**: All existing tests should pass after migration
