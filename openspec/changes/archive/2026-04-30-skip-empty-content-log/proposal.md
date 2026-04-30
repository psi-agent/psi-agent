## Why

Session 日志在 `content` 为空字符串时仍然打印日志行，产生无意义的空行日志。当 delta 中其他字段（如 `reasoning`）非空时，空的 `content` 日志是多余的。

## What Changes

- 修改 Session 日志逻辑：只有当 `content` 非空（不是 `None` 且不是空字符串）时才记录日志
- 同样适用于 `reasoning` 字段

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `session-response-logging`: 修改日志行为，空字符串不记录

## Impact

- `src/psi_agent/session/runner.py` - 修改 `_stream_conversation` 中的日志逻辑
