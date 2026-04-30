## Why

三个 channel（cli、repl、telegram）的日志风格与 session 不一致：
1. cli channel 不记录 `reasoning` 字段内容
2. repl channel 没有任何 stream 相关的日志
3. 日志格式不统一，难以调试和监控

## What Changes

- 统一三个 channel 的日志风格，与 session 保持一致
- 记录 `reasoning` 字段内容
- 记录 `content` 字段内容（非空时）
- 使用相同的日志格式和级别

## Capabilities

### New Capabilities

- `channel-stream-logging`: Channel 组件对流式响应的日志记录规范

### Modified Capabilities

（无）

## Impact

- `src/psi_agent/channel/cli/cli.py` - 添加 reasoning 日志
- `src/psi_agent/channel/repl/client.py` - 添加 stream 日志
- `src/psi_agent/channel/telegram/client.py` - 统一日志风格
