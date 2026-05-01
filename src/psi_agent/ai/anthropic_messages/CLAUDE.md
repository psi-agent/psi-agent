# psi_agent.ai.anthropic_messages

Anthropic Messages API 的协议转换适配器。

## 设计思路

**协议转换**：将 OpenAI chat completions 格式转换为 Anthropic Messages 格式，再将 Anthropic 响应转换回 OpenAI 格式。这种双向转换使得 psi-session 无需感知底层 API 差异。

**核心转换器**：`translator.py` 实现完整的双向转换逻辑，包括：
- 请求转换：OpenAI → Anthropic
- 响应转换：Anthropic → OpenAI
- 流式转换：Anthropic SSE events → OpenAI SSE chunks

## 核心组件

### AnthropicMessagesConfig

配置 dataclass，定义：

| 字段 | 类型 | 说明 |
|------|------|------|
| session_socket | str | Unix socket 路径（server 监听） |
| model | str | 默认模型名称 |
| api_key | str | Anthropic API 密钥 |
| base_url | str | API 基础 URL（可选） |

### AnthropicMessagesClient

Async context manager，核心方法：

```python
async def messages(
    self, request_body: dict[str, Any], stream: bool = False
) -> dict[str, Any] | AsyncGenerator[str]
```

**请求处理流程**：

1. 检查 `model` 字段，若缺失或为 `"session"` 则注入配置中的默认模型
2. 调用 `translate_openai_to_anthropic()` 转换请求格式
3. 发送请求到 Anthropic API
4. 调用 `translate_anthropic_to_openai()` 或 `translate_anthropic_stream()` 转换响应
5. 返回 OpenAI 格式的响应

### Translator

`translator.py` 提供完整的协议转换：

#### translate_openai_to_anthropic()

将 OpenAI 请求转换为 Anthropic 格式：

| OpenAI 字段 | Anthropic 字段 | 转换逻辑 |
|--------------|----------------|----------|
| messages (role=system) | system | 提取为独立参数 |
| messages (role=tool) | messages (role=user, tool_result) | 转换为 tool_result block |
| messages (tool_calls) | messages (content=tool_use) | 转换为 tool_use block |
| tools | tools | 转换 function schema 格式 |
| max_tokens | max_tokens | 直接传递 |
| reasoning_effort | output_config.effort | 映射到 output_config |

#### translate_anthropic_to_openai()

将 Anthropic 响应转换为 OpenAI 格式：

| Anthropic 字段 | OpenAI 字段 | 转换逻辑 |
|----------------|-------------|----------|
| content (text) | choices.message.content | 提取文本内容 |
| stop_reason | finish_reason | 映射：end_turn→stop, tool_use→tool_calls |
| usage.input_tokens | usage.prompt_tokens | 直接映射 |
| usage.output_tokens | usage.completion_tokens | 直接映射 |

#### StreamingTranslator

状态化的流式转换器，处理 Anthropic streaming events：

| Event Type | 输出 |
|------------|------|
| message_start | 初始 chunk（role=assistant） |
| content_block_start (tool_use) | tool_calls chunk（id, name） |
| content_block_start (thinking) | 无输出（内部记录） |
| content_block_start (redacted_thinking) | 无输出（标记跳过） |
| content_block_delta (text_delta) | content chunk |
| content_block_delta (thinking_delta) | reasoning_content chunk |
| content_block_delta (input_json_delta) | tool_calls.arguments chunk |
| message_delta (stop_reason) | finish_reason chunk |
| message_stop | [DONE] marker |

**状态管理**：

- `_message_id`：当前消息 ID
- `_model`：当前模型名称
- `_pending_tool_calls`：待处理的 tool calls（按 index）
- `_redacted_indices`：需要跳过的 redacted_thinking block indices

### Server & CLI

与 openai-completions 结构相同：

- Server：HTTP server，监听 Unix socket
- CLI：tyro CLI 入口，支持敏感参数掩码

## 接口定义

### 输入格式（OpenAI）

```json
{
  "model": "claude-3-5-sonnet",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 1000,
  "tools": [{"type": "function", "function": {"name": "read", "parameters": {...}}}]
}
```

### 内部格式（Anthropic）

```json
{
  "model": "claude-3-5-sonnet",
  "system": "You are helpful.",
  "messages": [
    {"role": "user", "content": [{"type": "text", "text": "Hello"}]}
  ],
  "max_tokens": 1000,
  "tools": [{"name": "read", "input_schema": {...}}]
}
```

### 输出格式（OpenAI）

与 openai-completions 输出格式相同。

## Tool Calls 转换

### OpenAI → Anthropic

OpenAI tool_calls 格式：

```json
{
  "role": "assistant",
  "content": "Let me help.",
  "tool_calls": [{
    "id": "call_123",
    "type": "function",
    "function": {"name": "read", "arguments": "{\"file\": \"test.py\"}"}
  }]
}
```

转换为 Anthropic tool_use blocks：

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "Let me help."},
    {"type": "tool_use", "id": "call_123", "name": "read", "input": {"file": "test.py"}}
  ]
}
```

### Anthropic → OpenAI

Anthropic tool_use → OpenAI tool_calls（流式）：

1. `content_block_start`：生成 tool_calls chunk（id, name, arguments=""）
2. `content_block_delta` (input_json_delta)：追加 arguments 字符串
3. `content_block_stop`：完成该 tool call

## Thinking Blocks 处理

Anthropic 支持两种 thinking block：

| 类型 | 处理方式 |
|------|----------|
| thinking | 转换为 `reasoning_content` 字段 |
| redacted_thinking | 跳过，不输出 |

流式处理：

```python
# content_block_delta (thinking_delta)
delta = {"type": "thinking_delta", "thinking": "..."}
# 输出
chunk = {"delta": {"reasoning_content": "..."}}
```

## 事件过滤

Anthropic SDK 可能发送非标准事件（如 `text` convenience event）。通过 `ANTHROPIC_STANDARD_EVENT_TYPES` 过滤：

```python
ANTHROPIC_STANDARD_EVENT_TYPES = frozenset({
    "message_start",
    "content_block_start",
    "content_block_delta",
    "content_block_stop",
    "message_delta",
    "message_stop",
    "ping",
})
```

## 测试覆盖

| 测试文件 | 覆盖内容 |
|----------|----------|
| test_config.py | 配置解析、默认值 |
| test_client.py | 请求发送、协议转换、错误处理 |
| test_server.py | HTTP 路由、流式/非流式响应 |
| test_cli.py | CLI 参数解析、掩码敏感参数 |
| test_translator.py | 完整协议转换测试（43KB） |

translator 测试覆盖所有转换场景：
- 消息转换（system, user, assistant, tool）
- Tool calls 双向转换
- Thinking blocks 处理
- 流式事件转换
- Redacted thinking 跳过
- 边界情况（空内容、无效 JSON）

## 与其他模块的关系

- **psi-session**：作为 client 调用本模块的 server
- **psi-ai.openai-completions**：兄弟模块，直接转发而非转换