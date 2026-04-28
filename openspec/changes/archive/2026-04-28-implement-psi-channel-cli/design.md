## Context

psi-channel-cli 是最简单的 channel 实现，作为 HTTP client 连接 psi-session 的 Unix socket，发送用户消息并输出响应。参考现有 psi-ai-openai-completions 的 client 实现。

## Goals / Non-Goals

**Goals:**
- 实现 CLI 工具，接收 session socket 路径和用户消息
- 发送 OpenAI chat completion 请求到 session
- 输出 agent 响应到 stdout
- 支持非流式和流式响应
- 单元测试覆盖

**Non-Goals:**
- 交互式 REPL（只处理单次请求）
- 多轮对话管理
- 复杂的输出格式化

## Decisions

### 使用 aiohttp 作为 HTTP client

**Rationale:** 与项目其他组件保持一致，支持 Unix socket 连接。

### CLI 参数设计

**设计：**
- `--session-socket`: session 的 Unix socket 路径
- `--message`: 用户消息内容
- `--stream`: 是否使用流式响应（默认 false）

### 输出格式

**设计：**
- 非流式：直接输出响应内容
- 流式：实时输出每个 chunk

## Risks / Trade-offs

- **Session 未启动** → 返回连接错误，提示用户启动 session
- **Socket 路径错误** → 返回连接错误