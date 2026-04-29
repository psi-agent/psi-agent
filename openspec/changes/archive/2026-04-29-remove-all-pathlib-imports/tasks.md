## 1. Test Files - Channel

- [x] 1.1 Update `tests/channel/repl/test_repl.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 1.2 Update `tests/channel/repl/test_config.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations

## 2. Test Files - Session

- [x] 2.1 Update `tests/session/test_workspace_watcher.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 2.2 Update `tests/session/test_server.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 2.3 Update `tests/session/test_runner.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations

## 3. Test Files - Workspace

- [x] 3.1 Update `tests/workspace/test_unpack.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 3.2 Update `tests/workspace/test_umount.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 3.3 Update `tests/workspace/test_snapshot.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 3.4 Update `tests/workspace/test_pack.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 3.5 Update `tests/workspace/test_mount.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations
- [x] 3.6 Update `tests/workspace/test_integration.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations

## 4. Test Files - AI

- [x] 4.1 Update `tests/ai/anthropic_messages/test_server.py` - Remove `from pathlib import Path as SyncPath`, remove `SyncPath` type annotations

## 5. Verification

- [x] 5.1 Run `rg "from pathlib import Path|import pathlib" tests/` to verify no pathlib imports remain
- [x] 5.2 Run `ruff check` to verify no lint errors
- [x] 5.3 Run `ruff format` to verify formatting
- [x] 5.4 Run `ty check` to verify type checking passes
- [x] 5.5 Run `pytest` to verify all tests pass
