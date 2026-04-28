## Why

当前的 `system.py` 约定使用模块级函数（`build_system_prompt()` 和 `compact_history()`），这导致无法管理状态。OpenClaw 的 compaction 需要保存 `previous_summary` 以支持增量摘要更新，但模块级函数无法持久化这个状态。

通过引入 `System` 类，可以让 workspace 管理自己的状态，session 启动时实例化一个 `System` 对象，该对象可以在多次 `compact_history()` 调用之间保持 `previous_summary`。

## What Changes

- 将 `system.py` 的约定从模块级函数改为 `System` 类
- `System` 类包含 `build_system_prompt()` 和 `compact_history()` 方法
- `System` 类可以管理内部状态（如 `previous_summary`）
- Session 启动时实例化 `System` 对象
- 同时增强 `compact_history()` 功能：
  - 支持增量摘要更新（`previous_summary`）
  - 完善消息序列化（处理 `thinking`、`toolCall`、`toolResult`）
  - 对 tool result 进行截断
  - 添加专门的摘要 system prompt

## Capabilities

### Modified Capabilities

- `workspace-systems`: 修改 `system.py` 约定，从模块级函数改为 `System` 类

## Impact

- `examples/an-openclaw-like-workspace/systems/system.py` - 重构为 `System` 类
- `examples/a-simple-bash-only-workspace/systems/system.py` - 重构为 `System` 类
- `src/psi_agent/session/` - Session 需要实例化 `System` 对象
- `CLAUDE.md` - 更新 `systems/system.py` 规范
