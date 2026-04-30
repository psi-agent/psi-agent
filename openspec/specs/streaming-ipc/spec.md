## Purpose

定义 psi-agent 组件间（Channel、Session、AI）的流式通信协议，确保实时响应输出和正确的 tool call 处理。

## Requirements

### Requirement: Channel 默认使用流式请求

Channel 组件 SHALL 默认使用流式（SSE）请求与 Session 通信，实现实时响应输出。

#### Scenario: REPL 发送流式请求
- **WHEN** 用户在 REPL 中输入消息
- **THEN** REPL SHALL 发送 `stream: true` 的请求给 Session
- **AND** 实时显示接收到的 SSE 内容块

#### Scenario: 流式响应实时显示
- **WHEN** Session 返回流式响应
- **THEN** Channel SHALL 逐块解析并显示内容
- **AND** 在收到 `[DONE]` 标记后结束显示

### Requirement: Channel 提供非流式 API 向后兼容

Channel 客户端 SHALL 保留非流式请求方法，供需要完整响应的场景使用。

#### Scenario: 使用非流式 API
- **WHEN** 调用 `send_message()` 方法
- **THEN** Channel SHALL 发送 `stream: false` 请求
- **AND** 等待完整响应后返回

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

Session SHALL 根据 Channel 请求决定是否流式返回响应。

#### Scenario: Channel 请求流式响应
- **WHEN** Channel 发送 `stream: true` 请求
- **THEN** Session SHALL 直接转发 AI 的流式响应给 Channel
- **AND** 隐藏 tool_calls 和 thinking 内容

#### Scenario: Channel 请求非流式响应
- **WHEN** Channel 发送 `stream: false` 请求
- **THEN** Session SHALL 收集完整响应后返回
- **AND** 返回过滤后的 OpenAI 格式响应

### Requirement: 流式错误处理

所有组件 SHALL 正确处理流式传输中的错误。

#### Scenario: 流式传输中发生错误
- **WHEN** 流式传输过程中发生错误
- **THEN** 组件 SHALL 通过 SSE 错误事件通知下游
- **AND** 记录错误日志

#### Scenario: 连接中断
- **WHEN** 流式连接中断
- **THEN** 接收方 SHALL 检测到连接关闭
- **AND** 记录警告日志
