## Context

当前 psi-agent 的流式通信已基本实现，但需要细化：

**当前状态**：
- AI 组件根据请求决定流式/非流式
- Session 内部默认流式调用 AI，但不返回 thinking/tool call 过程
- REPL 支持 `/quit` 和 `/stream` 命令
- CLI 默认非流式

**约束**：
- 保持 OpenAI chat completion 协议兼容性
- Thinking 和 tool call 输出需要特定格式，便于 Channel 解析和显示
- Telegram channel 暂不更新

## Goals / Non-Goals

**Goals:**
- Session 将 thinking 和 tool call 过程以特定格式返回给 Channel
- REPL 简化为纯消息转发，通过命令行参数控制流式
- CLI 默认流式，可通过参数切换
- 定义 thinking 输出格式约定

**Non-Goals:**
- 不修改 Telegram channel
- 不修改 AI 组件（已满足需求）
- 不修改底层通信协议

## Decisions

### Decision 1: Thinking 输出格式

**选择**：使用特殊标记包裹 thinking 和 tool call 内容。

**格式约定**：
```
<thinking>
[思考内容或 tool call 信息]
</thinking>
```

**理由**：
- 与 XML 类似，易于解析
- 不干扰正常内容显示
- Channel 可以选择显示或隐藏

**Tool call 格式**：
```
<thinking>
[Tool: tool_name]
Arguments: {"arg1": "value1"}
Result: [工具执行结果]
</thinking>
```

### Decision 2: Session 返回 thinking 的时机

**选择**：在流式模式下，thinking/tool call 内容作为独立的 SSE 事件发送。

**实现**：
- 每个 tool call 执行完成后，立即发送 thinking 块
- 最终 AI 响应正常流式返回
- 非流式模式下，thinking 内容放在响应的特定字段或前缀

### Decision 3: REPL 命令行参数

**选择**：添加 `--no-stream` 参数，默认流式。

**理由**：
- 符合"默认最佳体验"原则
- 用户通过 Ctrl+D/Ctrl+C 退出更自然
- 简化代码，移除命令解析逻辑

### Decision 4: CLI channel 默认流式

**选择**：CLI 默认 `stream: true`，添加 `--no-stream` 切换非流式。

**理由**：
- 与 REPL 行为一致
- 流式提供更好的用户体验

## Risks / Trade-offs

**[Risk] Thinking 内容过长** → Channel 可以选择折叠或隐藏 thinking 内容。

**[Risk] 格式解析复杂度** → 使用简单的 XML-like 标记，降低解析复杂度。

**[Risk] Breaking change for REPL** → 用户需要适应新的退出方式（Ctrl+D/Ctrl+C）。
