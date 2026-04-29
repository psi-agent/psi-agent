## Why

当前代码库混合使用 `pathlib.Path` 和 `anyio.Path`，虽然 IO 操作已使用 `anyio.Path`，但类型注解、路径操作和数据类存储仍使用 `pathlib.Path`。为了代码一致性和未来维护性，应该统一使用 `anyio.Path`。

## What Changes

- 将所有 `pathlib.Path` 类型注解替换为 `anyio.Path`
- 将所有 `from pathlib import Path` 替换为 `import anyio` 并使用 `anyio.Path`
- 将数据类中的 `Path` 类型字段改为 `anyio.Path`
- 更新所有路径操作使用 `anyio.Path` 的方法

### 受影响的文件：

**Config 文件** (类型注解):
- `src/psi_agent/channel/telegram/config.py`
- `src/psi_agent/channel/repl/config.py`
- `src/psi_agent/session/config.py`
- `src/psi_agent/ai/anthropic_messages/config.py`
- `src/psi_agent/ai/openai_completions/config.py`

**Session 文件** (类型注解和数据类):
- `src/psi_agent/session/schedule.py` - `Schedule.task_dir: Path`
- `src/psi_agent/session/workspace_watcher.py` - 返回类型和参数类型
- `src/psi_agent/session/tool_loader.py` - 返回类型和参数类型
- `src/psi_agent/session/runner.py` - 参数类型

**Workspace 文件** (类型注解):
- `src/psi_agent/workspace/snapshot/api.py`
- `src/psi_agent/workspace/umount/api.py`
- `src/psi_agent/workspace/mount/api.py`
- `src/psi_agent/workspace/unpack/api.py`
- `src/psi_agent/workspace/pack/api.py`

**AI 文件**:
- `src/psi_agent/ai/openai_completions/server.py`

## Capabilities

### New Capabilities

None - this is an internal refactoring for code consistency.

### Modified Capabilities

- `async-file-operations`: Update to require `anyio.Path` for ALL path-related code, including type annotations and data class fields.

## Impact

- **Breaking change for internal APIs**: Function signatures will change from `Path` to `anyio.Path`
- **No external API changes**: All public interfaces remain the same
- **Type checking**: May require updates to type annotations in tests
- **All tests must pass**: `ruff check`, `ruff format`, `ty check`, `pytest`
