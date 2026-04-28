## Context

当前实现从 session 传递 workspace 路径到 `build_system_prompt()`，这违反了 workspace 自包含的设计理念。`system.py` 位于 `workspace/systems/` 目录下，可以通过 `Path(__file__).parent.parent` 直接获取 workspace 路径。

## Goals / Non-Goals

**Goals:**
- 让 `system.py` 自己获取 workspace 路径
- 移除 session 中不必要的参数传递逻辑

**Non-Goals:**
- 改变 system prompt 的内容或格式

## Decisions

### 使用 `__file__` 获取 workspace 路径

**方案：** 在 `build_system_prompt()` 中使用 `Path(__file__).parent.parent` 获取 workspace 目录。

**原因：**
- `system.py` 位于 `workspace/systems/system.py`
- `Path(__file__).parent` = `workspace/systems/`
- `Path(__file__).parent.parent` = `workspace/`
- 无需外部传递，完全自包含

## Risks / Trade-offs

- 无风险，这是更简洁正确的实现
