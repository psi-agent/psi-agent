## 1. Update SessionConfig

- [x] 1.1 Make `workspace_path()` an async method that resolves and caches the absolute path
- [x] 1.2 Update `tools_dir()` to call the async `workspace_path()` method
- [x] 1.3 Update `systems_dir()` to call the async `workspace_path()` method

## 2. Update SessionRunner

- [x] 2.1 Update `__aenter__` to await `config.workspace_path()` and cache the result
- [x] 2.2 Pass the resolved absolute path to WorkspaceWatcher
- [x] 2.3 Pass the resolved absolute path to `_load_system()`
- [x] 2.4 Update `_handle_workspace_changes()` to use the cached resolved path

## 3. Update SessionServer

- [x] 3.1 Update `start()` to use the resolved workspace path for loading schedules
- [x] 3.2 Ensure the runner receives the resolved workspace path

## 4. Update WorkspaceWatcher

- [x] 4.1 Ensure WorkspaceWatcher uses the absolute workspace path passed during initialization
- [x] 4.2 Verify all subdirectory paths are derived from the absolute workspace path

## 5. Add Tests

- [x] 5.1 Test `workspace_path()` returns absolute path for relative input
- [x] 5.2 Test `workspace_path()` returns same path for absolute input
- [x] 5.3 Test `workspace_path()` caching works correctly
- [x] 5.4 Test WorkspaceWatcher uses correct paths with relative workspace input
- [x] 5.5 Test System class receives absolute workspace path

## 6. Verification

- [x] 6.1 Run `uv run ruff check` to verify lint passes
- [x] 6.2 Run `uv run ruff format` to verify formatting
- [x] 6.3 Run `uv run ty check` to verify type checking passes
- [x] 6.4 Run `uv run pytest` to verify all tests pass
