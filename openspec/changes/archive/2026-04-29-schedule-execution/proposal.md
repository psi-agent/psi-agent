## Why

psi-agent 的 workspace 设计中定义了 `schedules/` 目录用于定时任务，但 psi-session 尚未实现定时任务的加载和执行功能。实现此功能可以让 agent 按照预定的时间表自动执行任务（如每日摘要、定期清理等）。

## What Changes

- 在 psi-session 中添加 schedule 加载器，扫描 workspace 的 `schedules/` 目录
- 实现 cron 表达式解析，支持标准 5 字段 cron 格式
- 添加 schedule 执行器，按 cron 时间表触发任务
- 任务触发时将 TASK.md 内容作为用户消息发送给 LLM

## Capabilities

### New Capabilities

- `schedule-execution`: 定时任务加载和执行功能，支持 cron 表达式定义的时间表

### Modified Capabilities

- `session-core`: session 启动时需要加载并启动 schedule 执行器

## Impact

- **新代码**: `src/psi_agent/session/schedule.py` - schedule 加载器和执行器
- **修改代码**: `src/psi_agent/session/runner.py` - 集成 schedule 执行器
- **依赖**: 使用 Python 标准库或轻量级 cron 库（如 `croniter`）
