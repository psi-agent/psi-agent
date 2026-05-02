# psi_agent.ai.openai_completions

OpenAI 及兼容 API 的直接转发适配器。

## 设计思路

**直接转发**：不进行协议转换，直接使用 OpenAI SDK 发送请求。通过 `extra_body` 参数支持提供商特定的扩展参数（如 `thinking`、`reasoning_effort`）。

**参数分离**：将请求参数分为两类：
- SDK 标准参数：通过 `KNOWN_SDK_PARAMS` 识别，直接传给 SDK
- 提供商特定参数：通过 `extra_body` 传递，由底层 API 处理

## 模块结构

```
openai_completions/
├── __init__.py      # 导出 OpenAICompletionsClient, OpenAICompletionsServer, OpenAICompletionsConfig
├── config.py        # OpenAICompletionsConfig dataclass
├── client.py        # OpenAICompletionsClient async context manager
├── server.py        # OpenAICompletionsServer HTTP server
└── cli.py           # OpenaiCompletions CLI dataclass
```

## 核心组件

### OpenAICompletionsConfig

配置 dataclass，定义：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| session_socket | str | 必填 | Unix socket 路径（server 监听） |
| model | str | 必填 | 默认模型名称 |
| api_key | str | 必填 | API 密钥 |
| base_url | str | "https://api.openai.com/v1" | API 基础 URL |
| thinking | str \| None | None | 思考模式类型（"enabled"/"disabled"） |
| reasoning_effort | str \| None | None | 推理努力程度（"low"/"medium"/"high"） |

方法：
- `socket_path() -> anyio.Path`：返回 socket 路径的 anyio.Path 对象

### OpenAICompletionsClient

Async context manager，核心方法：

```python
async def chat_completions(
    self, request_body: dict[str, Any], stream: bool = False
) -> dict[str, Any] | AsyncGenerator[str]
```

**内部方法**：
- `_split_params(body) -> tuple[dict, dict | None]`：分离 SDK 参数和扩展参数
- `_non_stream_request(body) -> dict[str, Any]`：非流式请求
- `_stream_request(body) -> AsyncGenerator[str]`：流式请求
- `_handle_error(e) -> dict[str, Any]`：统一错误处理

**请求处理流程**：

1. 检查 `model` 字段，若缺失则注入配置中的默认模型
2. 记录请求信息（DEBUG 级别记录完整 body，INFO 级别记录摘要）
3. 调用 `_split_params()` 分离 SDK 参数和扩展参数
4. 发送请求（流式或非流式）
5. 返回响应或 yield SSE chunks

**流式请求日志**：

`_stream_request` 方法在发送请求前记录完整请求 body（DEBUG 级别），确保流式与非流式请求具有相同的日志粒度。

### OpenAICompletionsServer

HTTP server，监听 Unix socket：

- 路由：`POST /v1/chat/completions`
- 请求体：OpenAI chat completions 格式
- 响应：OpenAI chat completions 格式（非流式）或 SSE stream（流式）

**生命周期方法**：
- `start()`：移除已有 socket 文件、初始化 client、启动 server
- `stop()`：关闭 client、清理 runner

**请求处理**：
- 接收请求后注入配置中的 model
- 注入 thinking 和 reasoning_effort 参数（如果配置）
- 调用 client 处理请求

**流式响应日志**：

`_handle_streaming` 方法在流式完成后记录两条日志：
- DEBUG 级别："SSE stream completed successfully"
- INFO 级别："Streaming response completed"

### CLI 入口

```bash
psi-agent ai openai-completions \
  --session-socket ./ai.sock \
  --model gpt-4o \
  --api-key sk-xxx \
  --base-url https://api.openai.com/v1 \
  --thinking enabled \
  --reasoning-effort high
```

使用 tyro 从 dataclass 自动生成 CLI。

## 接口定义

### 请求格式

标准 OpenAI chat completions 格式：

```json
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.7,
  "max_tokens": 1000,
  "tools": [...],
  "thinking": {"type": "enabled", "budget_tokens": 10000}
}
```

### 响应格式

非流式：

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4o",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
}
```

流式：SSE chunks

```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","choices":[{"delta":{"content":"Hello"}}]}

data: [DONE]
```

## 参数分离机制

`KNOWN_SDK_PARAMS` 定义了 OpenAI SDK 接受的标准参数：

```python
KNOWN_SDK_PARAMS: set[str] = {
    "model", "messages", "temperature", "top_p", "n", "stream",
    "stop", "max_tokens", "presence_penalty", "frequency_penalty",
    "logit_bias", "user", "response_format", "tools", "tool_choice",
    "seed", "logprobs", "top_logprobs", "parallel_tool_calls",
    "stream_options", "service_tier", "modalities", "audio",
    "prediction", "metadata", "store",
}
```

`_split_params()` 方法将请求参数分为：
- `sdk_params`：在 KNOWN_SDK_PARAMS 中的参数，直接传给 SDK
- `extra_params`：不在 KNOWN_SDK_PARAMS 中的参数，通过 `extra_body` 传递

示例：

```python
# 请求中包含扩展参数
request_body = {
    "model": "claude-3-5-sonnet",
    "messages": [...],
    "thinking": {"type": "enabled", "budget_tokens": 10000}
}

# _split_params() 分离后
sdk_params = {"model": "claude-3-5-sonnet", "messages": [...]}
extra_params = {"thinking": {"type": "enabled", "budget_tokens": 10000}}

# SDK 调用
await client.chat.completions.create(**sdk_params, extra_body=extra_params)
```

## 错误处理

统一返回 `{error, status_code}` 格式：

```python
def _handle_error(self, e: Exception) -> dict[str, Any]:
    if isinstance(e, AuthenticationError):
        return {"error": "Authentication failed", "status_code": 401}
    if isinstance(e, RateLimitError):
        return {"error": "Rate limit exceeded", "status_code": 429}
    if isinstance(e, APITimeoutError):
        return {"error": "Request timeout", "status_code": 500}
    if isinstance(e, APIConnectionError):
        return {"error": "Connection failed", "status_code": 500}
    if isinstance(e, APIStatusError):
        return {"error": str(e), "status_code": e.status_code or 500}
    return {"error": str(e), "status_code": 500}
```

## 测试覆盖

| 测试文件 | 覆盖内容 |
|----------|----------|
| test_config.py | 配置创建、默认值、socket_path 方法 |
| test_client.py | context manager、流式/非流式请求、错误处理、参数分离、extra_body 传递 |
| test_server.py | 路由配置、请求处理、流式/非流式响应、thinking/reasoning_effort 注入 |
| test_cli.py | CLI 参数解析、mask_sensitive_args 调用、config 创建 |

## 与其他模块的关系

- **psi-session**：作为 client 调用本模块的 server
- **psi-ai.anthropic-messages**：兄弟模块，同样对外暴露 OpenAI 格式，但内部进行协议转换