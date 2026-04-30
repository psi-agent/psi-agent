## Why

当前 psi-agent 的组件间通信（Channel → Session → AI）在默认情况下使用非流式 HTTP 请求，导致用户需要等待完整响应生成后才能看到输出。将所有通信改为流式（SSE）可以显著改善用户体验，实现实时响应输出，让用户能够即时看到 LLM 的生成过程。

## What Changes

- **Channel → Session**：默认启用流式请求（`stream: true`），支持实时接收 SSE 响应
- **Session → AI**：默认使用流式请求调用 AI 组件，即使 Channel 未请求流式
- **Session 内部处理**：流式响应在 tool call 时需要完整收集后继续对话循环
- **BREAKING**：Channel 客户端 API 需要支持流式响应处理（`send_message_stream` 方法）

## Capabilities

### New Capabilities

- `streaming-ipc`: 组件间流式通信能力，定义 Channel、Session、AI 三者之间的流式交互协议

### Modified Capabilities

- `session-core`: 修改默认通信模式为流式，更新 streaming 响应处理逻辑
- `repl-channel`: 添加流式响应处理，实时显示 LLM 输出
- `psi-ai-openai-completions`: 确保流式请求作为默认模式

## Impact

- **Affected Code**:
  - `src/psi_agent/channel/repl/client.py` — 添加流式请求支持
  - `src/psi_agent/channel/repl/repl.py` — 实时显示流式输出
  - `src/psi_agent/session/runner.py` — 默认使用流式调用 AI
  - `src/psi_agent/session/server.py` — 流式响应处理优化
- **API Changes**: Channel 客户端新增 `send_message_stream()` 方法
- **Dependencies**: 无新依赖，使用现有 aiohttp SSE 支持
