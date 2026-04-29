## 1. Dependency Setup

- [x] 1.1 Add `platformdirs` to project dependencies in `pyproject.toml`

## 2. Source Code Changes

- [x] 2.1 Update `src/psi_agent/channel/repl/config.py` - Replace `from pathlib import Path as SyncPath` with `from platformdirs import user_cache_dir`
- [x] 2.2 Update `get_history_path()` method to use `user_cache_dir("psi-agent")` instead of `SyncPath.home() / ".cache" / "psi-agent"`

## 3. Examples Changes

- [x] 3.1 Update `examples/a-simple-bash-only-workspace/tools/bash.py` - Replace `from pathlib import Path` with `import anyio`, use `anyio.Path`
- [x] 3.2 Update `examples/a-simple-bash-only-workspace/systems/system.py` - Replace `from pathlib import Path` with `import anyio`, use `anyio.Path`
- [x] 3.3 Update `examples/an-openclaw-like-workspace/systems/system.py` - Replace `from pathlib import Path` with `import anyio`, use `anyio.Path`

## 4. Tests Changes

- [x] 4.1 Update `tests/workspace/test_unpack.py` - Keep `SyncPath` for fixture annotation, use `anyio.Path(tmp_path)` conversion
- [x] 4.2 Update `tests/workspace/test_umount.py` - Keep `SyncPath` for fixture annotation, use `anyio.Path(tmp_path)` conversion
- [x] 4.3 Update `tests/workspace/test_snapshot.py` - Keep `SyncPath` for fixture annotation, use `anyio.Path(tmp_path)` conversion
- [x] 4.4 Update `tests/workspace/test_pack.py` - Keep `SyncPath` for fixture annotation, use `anyio.Path(tmp_path)` conversion
- [x] 4.5 Update `tests/workspace/test_mount.py` - Keep `SyncPath` for fixture annotation, use `anyio.Path(tmp_path)` conversion
- [x] 4.6 Update `tests/workspace/test_integration.py` - Keep `SyncPath` for fixture annotation, use `anyio.Path(tmp_path)` conversion
- [x] 4.7 Update `tests/session/test_workspace_watcher.py` - Replace `from pathlib import Path` with `import anyio`, use `anyio.Path(tmp_path)` conversion
- [x] 4.8 Update `tests/session/test_runner.py` - Replace `from pathlib import Path` with `import anyio`
- [x] 4.9 Update `tests/session/test_server.py` - Replace `from pathlib import Path` with `import anyio`
- [x] 4.10 Update `tests/channel/repl/test_repl.py` - Already uses `SyncPath` correctly, verify no changes needed
- [x] 4.11 Update `tests/channel/repl/test_config.py` - Already uses `SyncPath` correctly, verify no changes needed
- [x] 4.12 Update `tests/ai/anthropic_messages/test_server.py` - Replace `from pathlib import Path` with `import anyio`

## 5. Verification

- [x] 5.1 Run `ruff check` to verify no lint errors
- [x] 5.2 Run `ruff format` to verify formatting
- [x] 5.3 Run `ty check` to verify type checking passes
- [x] 5.4 Run `pytest` to verify all tests pass
