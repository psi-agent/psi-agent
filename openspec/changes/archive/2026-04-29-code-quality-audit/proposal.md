## Why

对 psi-agent 代码库进行全面的质量审查，确保所有 Python 文件遵循 CLAUDE.md 中定义的编码规范。发现多处不符合规范的代码，需要修复以保持代码一致性和可维护性。

## What Changes

### 发现的问题

1. **缺少 `from __future__ import annotations`**
   - `tests/utils/__init__.py` - 缺少此导入

2. **使用 `pathlib.Path` 进行文件 IO 操作（应使用 `anyio.Path`）**
   - `src/psi_agent/session/history.py:69` - 使用 `Path(history_file)` 而非 `anyio.Path`
   - `src/psi_agent/session/history.py:83` - 使用 `Path(history.history_file)`
   - `src/psi_agent/session/server.py:194-199` - 使用 `socket_path.exists()` 和 `socket_path.unlink()` 同步方法
   - `src/psi_agent/workspace/snapshot/api.py:73` - 使用 `upper_dir.iterdir()` 同步方法

3. **测试文件缺少 `from __future__ import annotations`**
   - 多个测试文件缺少此导入（除了 `tests/utils/test_proctitle.py` 和 `tests/session/test_workspace_watcher.py`）

4. **`__init__.py` 文件缺少 `from __future__ import annotations`**
   - `src/psi_agent/utils/__init__.py` - 缺少此导入

## Capabilities

### New Capabilities

- `code-quality-enforcement`: 确保所有 Python 文件遵循 CLAUDE.md 中定义的编码规范

### Modified Capabilities

无现有 capability 需要修改。

## Impact

### 受影响的文件

**源代码文件（需要修复）：**
- `src/psi_agent/session/history.py` - 第 69、83 行
- `src/psi_agent/session/server.py` - 第 194-199 行
- `src/psi_agent/workspace/snapshot/api.py` - 第 73 行
- `src/psi_agent/utils/__init__.py` - 缺少 `from __future__ import annotations`

**测试文件（需要添加 `from __future__ import annotations`）：**
- `tests/__init__.py`
- `tests/ai/__init__.py`
- `tests/ai/anthropic_messages/__init__.py`
- `tests/ai/anthropic_messages/test_client.py`
- `tests/ai/anthropic_messages/test_config.py`
- `tests/ai/anthropic_messages/test_server.py`
- `tests/ai/anthropic_messages/test_translator.py`
- `tests/ai/openai_completions/__init__.py`
- `tests/ai/openai_completions/test_client.py`
- `tests/ai/openai_completions/test_config.py`
- `tests/ai/openai_completions/test_server.py`
- `tests/channel/__init__.py`
- `tests/channel/cli/test_cli.py`
- `tests/channel/repl/__init__.py`
- `tests/channel/repl/test_client.py`
- `tests/channel/repl/test_config.py`
- `tests/channel/repl/test_repl.py`
- `tests/channel/telegram/__init__.py`
- `tests/channel/telegram/test_client.py`
- `tests/channel/telegram/test_config.py`
- `tests/channel/telegram/test_split_message.py`
- `tests/session/__init__.py`
- `tests/session/schedule/__init__.py`
- `tests/session/schedule/test_cron.py`
- `tests/session/schedule/test_loader.py`
- `tests/session/schedule/test_schedule.py`
- `tests/session/test_history.py`
- `tests/session/test_runner.py`
- `tests/session/test_server.py`
- `tests/session/test_tool_executor.py`
- `tests/session/test_tool_loader.py`
- `tests/utils/__init__.py`
- `tests/workspace/__init__.py`
- `tests/workspace/test_integration.py`
- `tests/workspace/test_manifest.py`
- `tests/workspace/test_mount.py`
- `tests/workspace/test_pack.py`
- `tests/workspace/test_snapshot.py`
- `tests/workspace/test_umount.py`
- `tests/workspace/test_unpack.py`

### 不需要修改的文件

以下文件已正确遵循所有规范：
- 所有 `src/psi_agent/ai/` 下的文件
- 所有 `src/psi_agent/channel/` 下的文件
- `src/psi_agent/session/runner.py`
- `src/psi_agent/session/schedule.py`
- `src/psi_agent/session/tool_executor.py`
- `src/psi_agent/session/tool_loader.py`
- `src/psi_agent/session/types.py`
- `src/psi_agent/session/workspace_watcher.py`
- `src/psi_agent/workspace/manifest.py`
- `src/psi_agent/workspace/mount/api.py`
- `src/psi_agent/workspace/pack/api.py`
- `src/psi_agent/workspace/umount/api.py`
- `src/psi_agent/workspace/unpack/api.py`
