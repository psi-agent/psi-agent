## Why

Session 日志存在两个问题：
1. `content` 为空字符串时仍然打印日志行，导致大量无意义的空行日志
2. AI 返回的 `reasoning` 字段（思考内容）没有被记录，导致调试时看不到 LLM 的思考过程

## What Changes

- 修改 session 日志逻辑：只有当 `content` 非空时才记录
- 新增对 `reasoning` 字段的日志记录（如果存在且非空）
- 保持对 `tool_calls` 的日志记录

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `session-response-logging`: 修改日志行为，空字段不记录，新增 reasoning 字段记录

## Impact

- `src/psi_agent/session/runner.py` - 修改 `_process_request` 和 `_stream_conversation` 中的日志逻辑
