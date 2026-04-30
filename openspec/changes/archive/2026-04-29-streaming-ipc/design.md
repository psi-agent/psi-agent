## Context

当前 psi-agent 架构中，三个核心组件通过 HTTP over Unix socket 进行 IPC 通信：

```
Channel (client) → Session (server) → AI (server) → LLM API
```

**当前状态**：
- Channel 默认发送 `stream: false`，等待完整响应
- Session 在非流式模式下对 AI 也使用非流式请求
- 代码已支持流式，但未作为默认行为

**约束**：
- 必须保持 OpenAI chat completion 协议兼容性
- Tool call 处理需要完整响应后才能继续对话循环
- 不能引入新依赖

## Goals / Non-Goals

**Goals:**
- Channel 默认使用流式请求，实时显示 LLM 输出
- Session 默认对 AI 使用流式请求，即使 Channel 未请求流式
- 保持 tool call 处理的正确性（需要完整收集流式响应）
- 提供流式和非流式两种 API，向后兼容

**Non-Goals:**
- 不修改 AI 组件与上游 LLM API 的通信（已支持流式）
- 不修改 Telegram channel（单独处理）
- 不修改 workspace 相关功能

## Decisions

### Decision 1: Channel 默认使用流式请求

**选择**：Channel 客户端新增 `send_message_stream()` 方法，REPL 默认调用此方法。

**理由**：
- 用户可以实时看到 LLM 输出，改善体验
- 保持 `send_message()` 方法向后兼容，供非流式场景使用

**替代方案**：
- 修改 `send_message()` 直接返回流式 — 破坏现有 API
- 使用回调函数 — 增加复杂度

### Decision 2: Session 默认对 AI 使用流式请求

**选择**：`_run_conversation()` 改为默认使用流式调用 AI，内部收集完整响应。

**理由**：
- 统一处理路径，减少代码分支
- 流式响应可以提前检测到错误
- 为未来支持流式 tool call 做准备

**实现细节**：
- 流式响应在 Session 内部完整收集
- Tool call 需要完整响应才能执行
- 最终响应根据 Channel 请求决定是否流式返回

### Decision 3: 流式响应格式

**选择**：使用 SSE (Server-Sent Events) 格式，与 OpenAI API 一致。

**格式**：
```
data: {"choices":[{"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"choices":[{"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

**理由**：
- 与 OpenAI API 完全兼容
- 现有代码已支持此格式
- aiohttp 原生支持 SSE

## Risks / Trade-offs

**[Risk] Tool call 处理延迟** → 流式响应需要完整收集后才能处理 tool call，但这是必要开销，不影响最终结果正确性。

**[Risk] 错误处理复杂度** → 流式传输中发生错误时，需要通过 SSE 发送错误事件。保持现有错误处理逻辑，在流式开始前检测大部分错误。

**[Risk] 向后兼容性** → 保留非流式 API，Channel 可选择使用哪种模式。
