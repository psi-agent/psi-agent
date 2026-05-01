# psi_agent.ai.openai_completions

OpenAI 及兼容 API 的直接转发适配器。

## 设计思路

**直接转发**：不进行协议转换，直接使用 OpenAI SDK 发送请求。通过 `extra_body` 参数支持提供商特定的扩展参数（如 `thinking`、`reasoning_effort`）。

**参数分离**：将请求参数分为两类：
- SDK 标准参数：通过 `KNOWN_SDK_PARAMS` 识别，直接传给 SDK
- 提供商特定参数：通过 `extra_body` 传递，由底层 API 处理

## 核心组件

### OpenAICompletionsConfig

配置 dataclass，定义：

| 字段 | 类型 | 说明 |
|------|------|------|
| session_socket | str | Unix socket 路径（server 监听） |
| model | str | 默认模型名称 |
| api_key | str | API 密钥 |
| base_url | str | API 基础 URL |

### OpenAICompletionsClient

Async context manager，核心方法：

```python
async def chat_completions(
    self, request_body: dict[str, Any], stream: bool = False
) -> dict[str, Any] | AsyncGenerator[str]
```

**请求处理流程**：

1. 检查 `model` 字段，若缺失则注入配置中的默认模型
2. 记录请求信息（DEBUG 级别记录完整 body，INFO 级别记录摘要）
3. 调用 `_split_params()` 分离 SDK 参数和扩展参数
4. 发送请求（流式或非流式）
5. 返回响应或 yield SSE chunks

### OpenAICompletionsServer

HTTP server，监听 Unix socket：

- 路由：`POST /chat/completions`
- 请求体：OpenAI chat completions 格式
- 响应：OpenAI chat completions 格式（非流式）或 SSE stream（流式）

### CLI 入口

```bash
psi-agent ai openai-completions \
  --session-socket ./ai.sock \
  --model gpt-4o \
  --api-key sk-xxx \
  --base-url https://api.openai.com/v1
```

使用 tyro 从函数签名自动生成 CLI。

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

## 扩展参数支持

通过 `extra_body` 传递提供商特定参数：

| 参数 | 提供商 | 说明 |
|------|--------|------|
| thinking | Anthropic | 思考模式配置 |
| reasoning_effort | OpenAI | 推理努力程度 |

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
# client.py
def _handle_error(self, e: Exception) -> dict[str, Any]:
    if isinstance(e, AuthenticationError):
        return {"error": "Authentication failed", "status_code": 401}
    # ...
```

## 测试覆盖

| 测试文件 | 覆盖内容 |
|----------|----------|
| test_config.py | 配置解析、默认值 |
| test_client.py | 请求发送、响应处理、错误处理 |
| test_server.py | HTTP 路由、流式/非流式响应 |
| test_cli.py | CLI 参数解析、掩码敏感参数 |

## 与其他模块的关系

- **psi-session**：作为 client 调用本模块的 server
- **psi-ai.anthropic-messages**：兄弟模块，同样对外暴露 OpenAI 格式