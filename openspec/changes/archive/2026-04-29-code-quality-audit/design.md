## Context

psi-agent 项目在 CLAUDE.md 中定义了严格的编码规范，包括：
1. 所有 Python 文件必须以 `from __future__ import annotations` 开头
2. 所有文件 IO 操作必须使用 `anyio.Path` 的 async 方法，禁止使用 `pathlib.Path` 的同步方法

经过全面代码审查，发现部分文件未遵循这些规范。本设计文档描述如何修复这些问题。

## Goals / Non-Goals

**Goals:**
- 修复所有缺少 `from __future__ import annotations` 的文件
- 将所有使用 `pathlib.Path` 进行文件 IO 的代码改为使用 `anyio.Path`
- 确保所有修改后的代码通过 ruff check、ruff format 和 ty check

**Non-Goals:**
- 不重构代码逻辑
- 不添加新功能
- 不修改测试用例的测试逻辑

## Decisions

### 1. `from __future__ import annotations` 添加位置

**决策：** 在模块文档字符串之后、其他 import 之前添加。

**理由：** 符合 CLAUDE.md 规范要求，确保现代 PEP 604 联合语法在所有上下文中可用。

### 2. `pathlib.Path` 替换策略

**决策：** 将 `pathlib.Path` 的同步 IO 方法替换为 `anyio.Path` 的 async 方法。

**具体修改：**

| 文件 | 原代码 | 修改后 |
|------|--------|--------|
| `session/history.py:69` | `Path(history_file)` | `anyio.Path(history_file)` |
| `session/history.py:83` | `Path(history.history_file)` | `anyio.Path(history.history_file)` |
| `session/server.py:194-199` | `socket_path.exists()` / `socket_path.unlink()` | `await anyio.Path(socket_path).exists()` / `await anyio.Path(socket_path).unlink()` |
| `workspace/snapshot/api.py:73` | `upper_dir.iterdir()` | `async for ... in anyio.Path(upper_dir).iterdir()` |

**理由：** `anyio.Path` 提供跨 async 框架的异步文件操作抽象，避免阻塞事件循环。

### 3. 测试文件处理

**决策：** 为所有缺少 `from __future__ import annotations` 的测试文件添加此导入。

**理由：** 保持代码一致性，虽然测试文件不直接影响生产代码，但遵循统一规范有助于维护。

## Risks / Trade-offs

### Risk 1: `session/server.py` 中的同步方法调用

**风险：** `socket_path.exists()` 和 `socket_path.unlink()` 在 `start()` 方法中调用，需要改为 async。

**缓解：** `start()` 方法已经是 async，可以直接使用 `await anyio.Path(...)` 模式。

### Risk 2: `workspace/snapshot/api.py:73` 的 `iterdir()` 调用

**风险：** `any(upper_dir.iterdir())` 使用同步迭代器，需要改为 async 迭代。

**缓解：** 改为 `any([p async for p in anyio.Path(upper_dir).iterdir()])` 或使用 async generator 表达式。

### Risk 3: 测试文件大量修改

**风险：** 修改大量测试文件可能引入意外问题。

**缓解：** 只添加 import 语句，不修改测试逻辑。运行完整测试套件验证。
