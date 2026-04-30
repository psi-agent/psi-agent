## Why

当前流式实现需要进一步细化：1) Session 应将 thinking 和 tool call 过程以特定格式返回给 Channel，让用户看到完整的推理过程；2) REPL 应简化为纯消息转发，不支持任何命令；3) CLI channel 需要默认流式。

## What Changes

- **AI 组件**：保持现状，根据请求的 `stream` 参数决定流式或非流式访问上游 API
- **Session**：
  - 无论 Channel 是否请求流式，都流式调用 AI
  - 将 thinking 和 tool call 过程以特定格式拼接到响应中返回给 Channel
  - 支持流式和非流式两种模式返回给 Channel
- **REPL channel**：
  - **BREAKING** 移除 `/quit` 和 `/stream` 命令，简化为纯消息转发
  - 默认流式，通过命令行参数 `--no-stream` 切换非流式
  - Ctrl+D/Ctrl+C 退出
- **CLI channel**：默认流式，通过 `--no-stream` 参数切换非流式
- **Telegram channel**：暂不更新

## Capabilities

### New Capabilities

- `thinking-output-format`: 定义 thinking 和 tool call 的输出格式约定

### Modified Capabilities

- `streaming-ipc`: 更新 Session 行为，增加 thinking/tool call 输出
- `repl-channel`: 简化为纯消息转发，移除命令支持
- `session-core`: Session 默认流式调用 AI，返回 thinking 过程

## Impact

- **Affected Code**:
  - `src/psi_agent/session/runner.py` — 添加 thinking/tool call 格式化输出
  - `src/psi_agent/session/server.py` — 流式返回 thinking 过程
  - `src/psi_agent/channel/repl/repl.py` — 移除命令支持，添加命令行参数
  - `src/psi_agent/channel/repl/cli.py` — 添加 `--stream`/`--no-stream` 参数
  - `src/psi_agent/channel/cli/cli.py` — 默认流式，添加切换参数
- **API Changes**: REPL CLI 参数变化
- **Breaking Changes**: REPL 不再支持 `/quit` 和 `/stream` 命令
