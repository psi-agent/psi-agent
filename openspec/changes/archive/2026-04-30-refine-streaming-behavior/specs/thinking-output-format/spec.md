## Purpose

定义 Session 返回给 Channel 的 thinking 和 tool call 输出格式，让用户能看到完整的推理过程。

## ADDED Requirements

### Requirement: Thinking 输出使用 XML-like 标记

Session SHALL 使用 `<thinking>` 标签包裹 thinking 和 tool call 内容。

#### Scenario: Thinking 内容格式
- **WHEN** Session 需要返回 thinking 内容
- **THEN** 内容 SHALL 被包裹在 `<thinking>` 和 `</thinking>` 标签之间
- **AND** Channel 可以解析并选择显示或隐藏

#### Scenario: Thinking 标签解析
- **WHEN** Channel 收到包含 `<thinking>` 标签的内容
- **THEN** Channel SHALL 能够正确解析标签内容
- **AND** 标签外的内容正常显示

### Requirement: Tool call 输出格式

Session SHALL 以特定格式输出 tool call 信息。

#### Scenario: Tool call 输出
- **WHEN** Session 执行 tool call
- **THEN** 输出格式 SHALL 为：
```
<thinking>
[Tool: tool_name]
Arguments: {"arg": "value"}
Result: [执行结果]
</thinking>
```

#### Scenario: 多个 tool calls
- **WHEN** Session 执行多个 tool calls
- **THEN** 每个 tool call SHALL 输出独立的 thinking 块
- **AND** 按执行顺序排列

### Requirement: Thinking 内容流式返回

Session SHALL 在流式模式下实时返回 thinking 内容。

#### Scenario: 流式 thinking 返回
- **WHEN** tool call 执行完成
- **THEN** Session SHALL 立即发送 thinking 块
- **AND** 不等待后续 tool calls 或最终响应

#### Scenario: 非流式 thinking 返回
- **WHEN** Channel 请求非流式响应
- **THEN** thinking 内容 SHALL 作为消息内容的前缀返回
- **AND** 最终 AI 响应跟在 thinking 内容之后
