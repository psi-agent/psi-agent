# psi_agent.ai.anthropic_messages

Anthropic Messages API 的协议转换适配器。

## 设计思路

**协议转换**：将 OpenAI chat completions 格式转换为 Anthropic Messages 格式，再将 Anthropic 响应转换回 OpenAI 格式。这种双向转换使得 psi-session 无需感知底层 API 差异。

**核心转换器**：`translator.py` 实现完整的双向转换逻辑，包括：
- 请求转换：OpenAI → Anthropic
- 响应转换：Anthropic → OpenAI
- 流式转换：Anthropic SSE events → OpenAI SSE chunks

## 模块结构

```
anthropic_messages/
├── __init__.py      # 导出 AnthropicMessagesClient, AnthropicMessagesServer, AnthropicMessagesConfig
├── config.py        # AnthropicMessagesConfig dataclass
├── client.py        # AnthropicMessagesClient async context manager
├── server.py        # AnthropicMessagesServer HTTP server
├── cli.py           # AnthropicMessages CLI dataclass
└── translator.py    # 协议转换器
```

## 核心组件

### AnthropicMessagesConfig

配置 dataclass，定义：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| session_socket | str | 必填 | Unix socket 路径（server 监听） |
| model | str | 必填 | 默认模型名称（如 "claude-sonnet-4-20250514"） |
| api_key | str | 必填 | Anthropic API 密钥 |
| base_url | str | "https://api.anthropic.com" | API 基础 URL |
| max_tokens | int | 4096 | 默认最大 token 数 |
| thinking | str \| None | None | 思考模式类型（"enabled"/"disabled"） |
| reasoning_effort | str \| None | None | 推理努力程度（"low"/"medium"/"high"） |

方法：
- `socket_path() -> anyio.Path`：返回 socket 路径的 anyio.Path 对象

### AnthropicMessagesClient

Async context manager，核心方法：

```python
async def messages(
    self, request_body: dict[str, Any], stream: bool = False
) -> dict[str, Any] | AsyncGenerator[str]
```

**内部方法**：
- `_non_stream_request(body) -> dict[str, Any]`：非流式请求
- `_stream_request(body) -> AsyncGenerator[str]`：流式请求
- `_handle_error(e) -> dict[str, Any]`：统一错误处理

**请求处理流程**：

1. 检查 `model` 字段，若缺失或为 `"session"` 则注入配置中的默认模型
2. 记录请求信息
3. 发送请求到 Anthropic API
4. 调用 `translate_anthropic_to_openai()` 或 `translate_anthropic_stream()` 转换响应
5. 返回 OpenAI 格式的响应

**特殊处理**：
- 流式请求时移除 `stream` 参数（Anthropic SDK 的 `messages.stream()` 不接受此参数）
- 使用 `ANTHROPIC_STANDARD_EVENT_TYPES` 过滤非标准事件

### AnthropicMessagesServer

HTTP server，监听 Unix socket：

- 路由：`POST /v1/chat/completions`
- 接收 OpenAI 格式请求
- 调用 `translate_openai_to_anthropic()` 转换请求
- 注入 thinking 和 reasoning_effort 参数（如果配置）
- 调用 client 处理请求
- 返回 OpenAI 格式响应

### Translator

`translator.py` 提供完整的协议转换：

#### translate_openai_to_anthropic()

将 OpenAI 请求转换为 Anthropic 格式：

| OpenAI 字段 | Anthropic 字段 | 转换逻辑 |
|--------------|----------------|----------|
| messages (role=system) | system | 提取为独立参数 |
| messages (role=tool) | messages (role=user, tool_result) | 转换为 tool_result block |
| messages (tool_calls) | messages (content=tool_use) | 转换为 tool_use block |
| tools (type=function) | tools (input_schema) | 转换 function schema 格式 |
| max_tokens | max_tokens | 直接传递 |
| reasoning_effort | output_config.effort | 映射到 output_config |
| thinking | thinking | 直接传递 |

**关键转换逻辑**：

1. **System 消息**：提取第一条 system 消息作为 `system` 参数
2. **Tool Calls**：`tool_calls` 数组转换为 `tool_use` content blocks
3. **Tool Result**：`role=tool` 消息转换为 `role=user` + `tool_result` block
4. **Arguments 解析**：`arguments` JSON 字符串解析为 `input` 对象

#### translate_anthropic_to_openai()

将 Anthropic 响应转换为 OpenAI 格式：

| Anthropic 字段 | OpenAI 字段 | 转换逻辑 |
|----------------|-------------|----------|
| content (text) | choices.message.content | 提取文本内容，多 block 拼接 |
| stop_reason | finish_reason | 映射：end_turn→stop, tool_use→tool_calls, max_tokens→length |
| usage.input_tokens | usage.prompt_tokens | 直接映射 |
| usage.output_tokens | usage.completion_tokens | 直接映射 |

#### StreamingTranslator

状态化的流式转换器，处理 Anthropic streaming events：

**状态管理**：
- `_message_id`：当前消息 ID
- `_model`：当前模型名称
- `_pending_tool_calls`：待处理的 tool calls（按 index）
- `_redacted_indices`：需要跳过的 redacted_thinking block indices

**事件处理**：

| Event Type | 输出 |
|------------|------|
| message_start | 初始 chunk（role=assistant） |
| content_block_start (tool_use) | tool_calls chunk（id, name, arguments=""） |
| content_block_start (thinking) | 无输出（内部记录） |
| content_block_start (redacted_thinking) | 无输出（标记跳过） |
| content_block_start (text) | 无输出 |
| content_block_delta (text_delta) | content chunk |
| content_block_delta (thinking_delta) | reasoning_content chunk |
| content_block_delta (input_json_delta) | tool_calls.arguments chunk |
| content_block_delta (signature_delta) | 无输出（元数据） |
| content_block_stop | 清理 pending tool call 和 redacted index |
| message_delta (stop_reason) | finish_reason chunk |
| message_stop | [DONE] marker |

#### translate_anthropic_stream()

异步生成器函数，将 Anthropic SSE stream 转换为 OpenAI chunk stream：

```python
async def translate_anthropic_stream(
    anthropic_stream: AsyncGenerator[str],
) -> AsyncGenerator[str]:
    translator = StreamingTranslator()
    async for sse_event in anthropic_stream:
        # 解析 SSE 格式
        # 调用 translator.translate_event()
        # yield OpenAI chunk
```

### CLI 入口

```bash
psi-agent ai anthropic-messages \
  --session-socket ./ai.sock \
  --model claude-sonnet-4-20250514 \
  --api-key sk-ant-xxx \
  --max-tokens 4096 \
  --thinking enabled
```

## 接口定义

### 输入格式（OpenAI）

```json
{
  "model": "claude-3-5-sonnet",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Let me check.", "tool_calls": [{"id": "call_123", "type": "function", "function": {"name": "read", "arguments": "{\"file\": \"test.py\"}"}}]},
    {"role": "tool", "tool_call_id": "call_123", "content": "file content"}
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
    {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
    {"role": "assistant", "content": [{"type": "text", "text": "Let me check."}, {"type": "tool_use", "id": "call_123", "name": "read", "input": {"file": "test.py"}}]},
    {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_123", "content": "file content"}]}
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

### Anthropic → OpenAI（流式）

1. `content_block_start (tool_use)`：生成 tool_calls chunk（id, name, arguments=""）
2. `content_block_delta (input_json_delta)`：追加 arguments 字符串
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
ANTHROPIC_STANDARD_EVENT_TYPES: frozenset[str] = frozenset({
    "message_start",
    "content_block_start",
    "content_block_delta",
    "content_block_stop",
    "message_delta",
    "message_stop",
    "ping",
})
```

非标准事件在 DEBUG 日志中记录后被跳过。

## 错误处理

与 openai-completions 相同的错误处理模式，返回 `{error, status_code}` 格式。

## 测试覆盖

| 测试文件 | 覆盖内容 |
|----------|----------|
| test_config.py | 配置创建、默认值、socket_path 方法 |
| test_client.py | context manager、流式/非流式请求、错误处理、model 注入和替换、事件过滤 |
| test_server.py | 路由配置、请求处理、流式/非流式响应、thinking/reasoning_effort 注入 |
| test_cli.py | CLI 参数解析、mask_sensitive_args 调用、config 创建 |
| test_translator.py | 完整协议转换测试（见下文） |

### translator 测试覆盖

`test_translator.py` 包含详尽的测试用例：

**请求转换**：
- 基本文本消息
- System 消息提取
- 多消息处理
- 参数传递
- Content block 透传
- 默认 max_tokens
- Tools 格式转换（OpenAI → Anthropic）
- Tools 格式透传（已是 Anthropic 格式）
- Tool result 消息转换
- Assistant 消息带 tool_calls 和文本
- Tool result 非字符串内容转换
- System 消息带 content blocks
- 非字符串内容转换
- 空消息列表
- 只有 system 消息

**响应转换**：
- 基本响应
- Usage 映射
- Finish reason 映射
- 多 content blocks 拼接

**流式转换**：
- message_start 事件
- content_block_delta 事件
- message_stop 事件
- message_delta 带 stop_reason
- 忽略的事件类型
- 空文本无输出
- 未知事件类型

**Tool Calls 流式**：
- content_block_start tool_use
- content_block_delta input_json_delta
- content_block_stop 清理 pending tool
- message_delta tool_use finish_reason

**Thinking 支持**：
- thinking_delta → reasoning_content
- signature_delta 无输出
- redacted_thinking 跳过
- 多 thinking deltas
- text_delta 带类型区分

**参数映射**：
- reasoning_effort → output_config.effort
- thinking 透传

## 与其他模块的关系

- **psi-session**：作为 client 调用本模块的 server
- **psi-ai.openai-completions**：兄弟模块，直接转发而非转换