## Why

Session 的日志在处理 AI 响应时，只记录 `content` 字段的前 100 字符，导致思考内容（thinking）、工具调用（tool_calls）等重要信息在日志中不可见或显示为 "..."。这使得调试和监控变得困难，无法完整了解 AI 的响应内容。

## What Changes

- 修改 `session/runner.py` 中的日志逻辑，完整记录所有响应字段
- 记录 `content`、`tool_calls`、`reasoning_content`（如果存在）等字段
- 对于空字段，跳过日志记录
- 对于非空字段，记录完整内容或更长的摘要

## Capabilities

### New Capabilities

- `session-response-logging`: Session 组件对 AI 响应的完整日志记录能力

### Modified Capabilities

- `defensive-coding`: 扩展现有规范，增加日志记录时的 null-safety 要求

## Impact

- `src/psi_agent/session/runner.py` - 修改 `_process_request` 和 `_stream_conversation` 中的日志逻辑
- 日志输出量会增加，但仍在 DEBUG 级别，不影响生产环境性能
