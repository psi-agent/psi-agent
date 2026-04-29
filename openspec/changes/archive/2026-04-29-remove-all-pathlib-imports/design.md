## Context

Currently, test files use `from pathlib import Path as SyncPath` for type annotations on pytest's `tmp_path` fixture. The fixture returns `pathlib.Path`, but we can simply not annotate the type (let pytest infer it) or use `anyio.Path` and convert immediately.

Files affected:
- `tests/channel/repl/test_repl.py`
- `tests/channel/repl/test_config.py`
- `tests/session/test_workspace_watcher.py`
- `tests/session/test_server.py`
- `tests/session/test_runner.py`
- `tests/workspace/test_unpack.py`
- `tests/workspace/test_umount.py`
- `tests/workspace/test_snapshot.py`
- `tests/workspace/test_pack.py`
- `tests/workspace/test_mount.py`
- `tests/workspace/test_integration.py`
- `tests/ai/anthropic_messages/test_server.py`

## Goals / Non-Goals

**Goals:**
- Remove all `from pathlib import Path as SyncPath` imports
- Remove `SyncPath` type annotations from test fixtures
- Convert `tmp_path` to `anyio.Path` immediately in test function bodies

**Non-Goals:**
- Changing test behavior
- Modifying source code (already clean)

## Decisions

### Remove type annotations for `tmp_path` fixture

**Rationale**: pytest's `tmp_path` fixture has a well-known return type. We don't need to annotate it - pytest will infer the type. Inside the test function, we immediately convert to `anyio.Path` for actual use.

**Alternative considered**: Keep `SyncPath` annotation and convert inside. Rejected because it leaves `pathlib` imports in the codebase, which we want to eliminate entirely.

### Implementation pattern

Before:
```python
from pathlib import Path as SyncPath

async def test_something(self, tmp_path: SyncPath) -> None:
    workspace = anyio.Path(tmp_path)
    ...
```

After:
```python
async def test_something(self, tmp_path) -> None:
    workspace = anyio.Path(tmp_path)
    ...
```

Or if we want type annotations:
```python
async def test_something(self, tmp_path: anyio.Path) -> None:
    # pytest still passes pathlib.Path, but we treat it as anyio.Path
    # This works because anyio.Path can wrap pathlib.Path
    ...
```

## Risks / Trade-offs

**Risk**: Type checkers might complain about `tmp_path: anyio.Path` annotation since pytest passes `pathlib.Path`.

**Mitigation**: Either remove the annotation (let pytest infer) or accept the minor type mismatch - the conversion is safe.
