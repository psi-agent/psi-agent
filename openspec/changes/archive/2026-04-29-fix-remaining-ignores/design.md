## Context

代码库中还有以下被忽略的检查：

1. **`__main__.py:37`** - `# ty: ignore[no-matching-overload]` - tyro 库不接受 Union 类型
2. **`telegram/bot.py:80,84,92`** - `# ty: ignore` - `updater` 属性可能为 None
3. **`examples/.../system.py:3`** - `# ruff: noqa: E501` - 行过长
4. **`tests/.../test_cron.py:120`** - `# noqa: E402` - import 在代码后

## Goals / Non-Goals

**Goals:**
- 修复 telegram/bot.py 中的 3 处 ty ignore（通过 assert）
- 修复 examples 中的 E501 忽略（拆分长行）
- 修复 tests 中的 E402 忽略（移动 import）
- 创建 tyro issue 复现示例

**Non-Goals:**
- 修复 tyro 库的类型问题（需要向 tyro 提交 PR）
- 修改第三方库

## Decisions

### Decision 1: 使用 assert 解决 telegram updater 类型问题

**Rationale:** `Application.updater` 的类型注解可能是 `None`，但在 `start()` 方法中我们已经初始化了 `_app`，所以 `updater` 不会为 `None`。添加 `assert self._app is not None` 和 `assert self._app.updater is not None` 可以帮助类型检查器理解这一点。

### Decision 2: 拆分长行解决 E501

**Rationale:** `system.py` 中的长行是字符串字面量，可以使用字符串拼接或括号内的隐式拼接来拆分。

### Decision 3: 移动 import 到文件顶部

**Rationale:** `test_cron.py` 中的 `from pathlib import Path` 应该在文件顶部导入，不需要延迟导入。

## Risks / Trade-offs

- **Risk:** assert 语句在生产环境中可能被优化掉（`python -O`）
  - **Mitigation:** 这只是类型检查辅助，运行时逻辑不变
