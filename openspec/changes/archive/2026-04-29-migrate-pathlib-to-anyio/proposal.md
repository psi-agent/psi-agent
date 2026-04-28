## Why

当前代码库中大量使用 `pathlib.Path` 进行文件系统操作，但这些操作都是**同步的**（blocking），违反了项目的 async 规范。psi-agent 是一个异步框架，所有 IO 操作应使用 async 生态方法。anyio 提供了 `anyio.Path` —— 一个异步版本的 Path，支持所有 pathlib.Path 的操作但以 async 方式执行。

## What Changes

- 将所有使用 `pathlib.Path` 进行同步文件操作的地方迁移到 `anyio.Path`
- 具体涉及的同步操作包括：
  - `Path.read_bytes()` → `await anyio.Path(...).read_bytes()`
  - `Path.read_text()` → `await anyio.Path(...).read_text()`
  - `Path.write_text()` → `await anyio.Path(...).write_text()`
  - `Path.exists()` → `await anyio.Path(...).exists()`
  - `Path.is_file()` → `await anyio.Path(...).is_file()`
  - `Path.is_dir()` → `await anyio.Path(...).is_dir()`
  - `Path.iterdir()` → `await anyio.Path(...).iterdir()` (返回 AsyncGenerator)
  - `Path.mkdir()` → `await anyio.Path(...).mkdir()`
  - `Path.unlink()` → `await anyio.Path(...).unlink()`
  - `Path.rmdir()` → `await anyio.Path(...).rmdir()`
  - `Path.resolve()` → `await anyio.Path(...).resolve()`

## Capabilities

### New Capabilities

无新增能力。此变更仅为内部实现改进，不引入新功能。

### Modified Capabilities

无修改的能力。此变更不改变任何 spec 级别的行为要求，仅改进实现细节。

## Impact

**受影响的文件（17个）**：

| 文件 | 同步操作 | 改造难度 |
|------|----------|----------|
| `psi_agent/session/tool_loader.py` | `read_bytes()`, `exists()`, `iterdir()`, `is_file()` | 中 - 需将函数改为 async |
| `psi_agent/session/workspace_watcher.py` | `read_bytes()`, `exists()`, `iterdir()`, `is_file()`, `is_dir()` | 中 - 需将函数改为 async |
| `psi_agent/session/history.py` | `exists()`, `read_text()`, `write_text()` | 中 - 需将函数改为 async |
| `psi_agent/session/schedule.py` | `exists()`, `iterdir()`, `is_dir()` | 低 - 已部分使用 anyio |
| `psi_agent/session/runner.py` | `exists()` | 低 - 仅一处 |
| `psi_agent/channel/repl/repl.py` | `exists()`, `mkdir()`, `parent` 属性 | 低 - 简单改造 |
| `psi_agent/workspace/mount/api.py` | `exists()`, `is_file()`, `mkdir()`, `resolve()` | 中 - 多处使用 |
| `psi_agent/workspace/pack/api.py` | `exists()`, `is_dir()`, `mkdir()`, `resolve()`, `iterdir()`, `is_file()` | 中 - 多处使用 |
| `psi_agent/workspace/snapshot/api.py` | `resolve()`, `exists()` | 低 - 已部分使用 anyio |
| `psi_agent/workspace/umount/api.py` | `resolve()`, `unlink()`, `rmdir()`, `iterdir()` | 低 - 已部分使用 anyio |
| `psi_agent/workspace/unpack/api.py` | `resolve()`, `exists()` | 低 - 简单改造 |
| `psi_agent/session/config.py` | 仅类型注解和 Path() 构造 | 无需改造 - 仅作为路径表示 |
| `psi_agent/ai/openai_completions/config.py` | 仅类型注解和 Path() 构造 | 无需改造 |
| `psi_agent/ai/anthropic_messages/config.py` | 仅类型注解和 Path() 构造 | 无需改造 |
| `psi_agent/channel/repl/config.py` | 仅类型注解和 Path() 构造 | 无需改造 |
| `psi_agent/channel/telegram/config.py` | 仅类型注解和 Path() 构造 | 无需改造 |
| `psi_agent/ai/openai_completions/server.py` | 仅 Path() 构造用于 socket 删除 | 低 - 改用 anyio.Path |

**API 影响**：无公开 API 变化，所有改动为内部实现。

**依赖影响**：无新增依赖，anyio 已是项目依赖。

**测试影响**：需更新相关单元测试以支持 async 函数。