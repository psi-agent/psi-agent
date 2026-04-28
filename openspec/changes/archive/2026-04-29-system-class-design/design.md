## Context

当前的 `system.py` 约定使用模块级函数：
- `build_system_prompt()` - 构建系统提示词
- `compact_history()` - 压缩对话历史

这种设计无法管理状态。OpenClaw 的 compaction 功能需要保存 `previous_summary` 以支持增量摘要更新，但模块级函数无法持久化这个状态。

## Goals / Non-Goals

**Goals:**
- 将 `system.py` 约定从模块级函数改为 `System` 类
- `System` 类可以管理内部状态（如 `previous_summary`）
- Session 启动时实例化 `System` 对象
- 增强 `compact_history()` 功能（增量更新、消息序列化、截断等）

**Non-Goals:**
- 不修改 psi-ai-* 组件
- 不实现 File Operations 追踪

## Decisions

### 1. System 类设计

**决定：** 使用类封装所有系统功能

```python
class System:
    """Workspace system configuration and state management."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir
        self._previous_summary: str | None = None

    async def build_system_prompt(
        self,
        is_main_session: bool = True,
        model: str = "unknown",
        timezone: str = "UTC",
    ) -> str:
        ...

    async def compact_history(
        self,
        history: list[dict[str, Any]],
        complete_fn: CompleteFn,
        max_tokens: int = 4000,
        keep_recent_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        ...
```

**理由：**
- 类可以管理状态（`_previous_summary`）
- Session 只需实例化一次，多次调用共享状态
- 符合面向对象设计原则

### 2. Session 侧的集成

Session 启动时：
```python
from systems.system import System

system = System(workspace_dir)
```

### 3. 增量摘要更新

当存在 `_previous_summary` 时，使用 `UPDATE_SUMMARIZATION_PROMPT`：
- 保留之前摘要中的信息
- 合并新的进度和决策
- 更新 "Next Steps"

### 4. 消息序列化改进

处理以下消息块类型：
- `thinking`: 显示为 `[Assistant thinking]: ...`
- `toolCall` / `tool_call`: 显示为 `[Assistant tool calls]: tool_name(arg1=value1, ...)`
- `toolResult` / `tool_result`: 显示为 `[Tool result]: ...`（截断到 2000 字符）

### 5. Tool Result 截断

对 tool result 内容截断到最大 2000 字符，避免摘要请求过大。

### 6. 摘要 System Prompt

使用 OpenClaw 的 `SUMMARIZATION_SYSTEM_PROMPT`：
```
You are a context summarization assistant. Your task is to read a conversation
between a user and an AI coding assistant, then produce a structured summary
following the exact format specified.

Do NOT continue the conversation. Do NOT respond to any questions in the
conversation. ONLY output the structured summary.
```

## Risks / Trade-offs

- **破坏性变更** → 需要更新所有 workspace 的 `system.py`
- **Session 需要修改** → 需要实例化 `System` 对象
- **增量摘要可能累积错误** → 可接受的 trade-off
