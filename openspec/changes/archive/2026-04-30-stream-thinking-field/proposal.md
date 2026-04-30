## Why

Session 当前将思考内容（reasoning 和工具调用）包装在 `<thinking>` 标签中作为 `content` 字段发送给 channel。这导致：
1. Channel 无法区分思考内容和最终回答
2. 思考内容被嵌入在 content 中，而不是作为独立字段
3. Channel 无法正确处理/显示思考过程

## What Changes

- 修改 Session 流式响应格式，将 AI 返回的 `reasoning` 字段直接流式转发给 channel
- 工具调用过程作为 `reasoning` 字段发送
- `content` 字段保持原样：AI 返回什么 content 就转发什么 content（包括 tool_calls 时的 content）
- Channel 可以根据 `reasoning` 字段独立处理思考过程

## Capabilities

### New Capabilities

- `stream-reasoning-field`: Session 在流式响应中转发 AI 的 reasoning 字段，并将工具调用过程也作为 reasoning 发送

### Modified Capabilities

（无）

## Impact

- `src/psi_agent/session/runner.py` - 修改 `_stream_conversation` 方法，流式转发 reasoning 字段
- `src/psi_agent/channel/cli/cli.py` - 可能需要更新以处理 reasoning 字段
- `src/psi_agent/channel/repl/client.py` - 可能需要更新以处理 reasoning 字段
- `src/psi_agent/channel/telegram/client.py` - 可能需要更新以处理 reasoning 字段
