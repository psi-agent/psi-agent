## MODIFIED Requirements

### Requirement: Session 默认对 AI 使用流式请求

Session 组件 SHALL 默认使用流式请求调用 AI 组件，无论 Channel 是否请求流式。

#### Scenario: Session 流式调用 AI
- **WHEN** Session 需要调用 AI 进行推理
- **THEN** Session SHALL 发送 `stream: true` 请求给 AI 组件
- **AND** 内部收集完整响应用于后续处理

#### Scenario: Tool call 需要完整响应
- **WHEN** AI 返回包含 tool_calls 的流式响应
- **THEN** Session SHALL 完整收集所有流式块
- **AND** 重构 tool_calls 后执行工具

### Requirement: Session 流式响应转发

Session SHALL 根据 Channel 请求决定是否流式返回响应，并包含 thinking 过程。

#### Scenario: Channel 请求流式响应
- **WHEN** Channel 发送 `stream: true` 请求
- **THEN** Session SHALL 流式转发 AI 响应给 Channel
- **AND** 在 tool call 执行后立即发送 thinking 块
- **AND** 隐藏 tool_calls 原始数据

#### Scenario: Channel 请求非流式响应
- **WHEN** Channel 发送 `stream: false` 请求
- **THEN** Session SHALL 收集完整响应后返回
- **AND** thinking 内容作为消息前缀返回
- **AND** 返回过滤后的 OpenAI 格式响应
