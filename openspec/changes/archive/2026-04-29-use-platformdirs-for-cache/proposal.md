## Why

Currently, there are still `pathlib.Path` imports in the codebase:
- `src/psi_agent/channel/repl/config.py` uses `pathlib.Path.home()` to construct the default history file path
- `examples/` and `tests/` directories have multiple `pathlib.Path` imports that should use `anyio.Path` for async file operations

Using `platformdirs` provides a cross-platform, standards-compliant way to determine user cache directories. For other path operations, `anyio.Path` should be used consistently for async file operations.

## What Changes

- Replace `pathlib.Path.home() / ".cache" / "psi-agent" / "repl_history.txt"` with `platformdirs.user_cache_dir("psi-agent")` for determining the default history file location
- Add `platformdirs` as a project dependency
- Replace all `pathlib.Path` imports in `examples/` with `anyio.Path`
- Replace all `pathlib.Path` imports in `tests/` with `anyio.Path` (using `from pathlib import Path as SyncPath` only for pytest's `tmp_path` fixture type annotations)

## Capabilities

### New Capabilities

- `platform-cache-dirs`: Standardized cross-platform cache directory resolution using platformdirs library

### Modified Capabilities

None - this is an internal implementation change with no API-level behavior changes.

## Impact

- **Affected Code**:
  - `src/psi_agent/channel/repl/config.py`
  - `examples/a-simple-bash-only-workspace/tools/bash.py`
  - `examples/a-simple-bash-only-workspace/systems/system.py`
  - `examples/an-openclaw-like-workspace/systems/system.py`
  - Multiple test files in `tests/`
- **Dependencies**: Add `platformdirs` to project dependencies
- **Behavior**: Default history file path will now use platform-specific cache directories (e.g., `~/.cache/psi-agent/` on Linux, `~/Library/Caches/psi-agent/` on macOS, `%LOCALAPPDATA%\psi-agent\` on Windows)
