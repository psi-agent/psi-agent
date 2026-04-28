## Why

The codebase contains several files that use `pathlib.Path` for file I/O operations, which are synchronous and block the event loop. According to the project's CLAUDE.md guidelines, all I/O operations must use async methods from `anyio.Path` to avoid blocking the async event loop. This is a code quality and performance issue that affects the responsiveness of the psi-agent framework.

## What Changes

- Replace synchronous `pathlib.Path` I/O operations with async `anyio.Path` equivalents in:
  - `examples/a-simple-bash-only-workspace/systems/system.py` - Uses `Path.read_text()`, `Path.exists()`, `Path.iterdir()`, `Path.is_dir()` synchronously
  - `examples/an-openclaw-like-workspace/systems/system.py` - Uses `Path.exists()` synchronously in `_read_bootstrap_file()`

- Specific operations to migrate:
  - `path.read_text()` → `await anyio.Path(path).read_text()`
  - `path.exists()` → `await anyio.Path(path).exists()`
  - `path.iterdir()` → `async for item in anyio.Path(path).iterdir()`
  - `path.is_dir()` → `await anyio.Path(path).is_dir()`
  - `path.is_file()` → `await anyio.Path(path).is_file()`

## Capabilities

### New Capabilities

- `async-file-operations`: Ensure all file I/O operations in example workspace system.py files use async anyio.Path methods

### Modified Capabilities

None - This is a code quality fix that doesn't change the external behavior or requirements.

## Impact

- **Affected Files**:
  - `examples/a-simple-bash-only-workspace/systems/system.py`
  - `examples/an-openclaw-like-workspace/systems/system.py`

- **Dependencies**: Already imports `anyio` in the affected files or needs to add it

- **Testing**: Existing tests should continue to pass; the async operations are functionally equivalent

- **Performance**: Improves async performance by not blocking the event loop during file operations
