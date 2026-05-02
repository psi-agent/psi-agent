# psi_agent.ai

LLM 提供商适配层，将不同 LLM 提供商的 API 转换为统一的 OpenAI chat completions 格式。

## 架构概述

psi-ai 模块采用**适配器模式**，包含两个独立的 LLM 提供商适配器：

| 适配器 | 提供商 | 职责 |
|--------|--------|------|
| openai-completions | OpenAI 及兼容 API | 直接转发请求，支持提供商特定参数 |
| anthropic-messages | Anthropic | 协议转换（OpenAI ↔ Anthropic Messages） |

### 统一接口

所有适配器对外暴露统一的 OpenAI chat completions 格式：

- **请求格式**：OpenAI chat completions API 格式
- **响应格式**：OpenAI chat completions API 格式
- **流式响应**：OpenAI SSE chunk 格式
- **通信协议**：HTTP over Unix socket

这种设计使得 psi-session 可以与任何 LLM 提供商通信，无需关心底层 API 差异。

## 组件关系

```
psi-session (client)
    │
    │ POST /v1/chat/completions (OpenAI format, HTTP over Unix socket)
    │
    ▼
psi-ai-* (server)
    │
    │ Provider-specific API
    │
    ▼
LLM Provider (OpenAI / Anthropic / others)
```

**通信协议**：

- psi-session 作为 HTTP client
- psi-ai-* 作为 HTTP server（监听 Unix socket）
- 请求/响应均使用 OpenAI chat completions JSON 格式
- 流式响应使用 SSE (Server-Sent Events)

## 模块结构

```
src/psi_agent/ai/
├── __init__.py          # Commands dataclass for CLI subcommands
├── CLAUDE.md            # 本文档
├── openai_completions/
│   ├── __init__.py      # 导出 Client, Server, Config
│   ├── client.py        # OpenAICompletionsClient
│   ├── server.py        # OpenAICompletionsServer
│   ├── config.py        # OpenAICompletionsConfig
│   ├── cli.py           # OpenaiCompletions CLI dataclass
│   └── CLAUDE.md        # OpenAI 适配器文档
└── anthropic_messages/
    ├── __init__.py      # 导出 Client, Server, Config
    ├── client.py        # AnthropicMessagesClient
    ├── server.py        # AnthropicMessagesServer
    ├── config.py        # AnthropicMessagesConfig
    ├── cli.py           # AnthropicMessages CLI dataclass
    ├── translator.py    # 协议转换器
    └── CLAUDE.md        # Anthropic 适配器文档
```

## 设计一致性

两个适配器遵循统一的设计模式：

### 文件结构一致

每个适配器包含相同的文件：
- `config.py` — 配置 dataclass
- `client.py` — Async context manager client
- `server.py` — HTTP server（Unix socket）
- `cli.py` — tyro CLI 入口
- `__init__.py` — 导出公共接口

### Async Context Manager 模式

```python
async with Client(config) as client:
    response = await client.chat_completions(request_body)
```

- `__aenter__`：初始化 SDK client，记录 DEBUG 日志
- `__aexit__`：关闭 SDK client，置空资源变量，记录 DEBUG 日志

### 统一错误处理

所有错误返回 `{error: str, status_code: int}` 格式：

| 错误类型 | status_code |
|----------|-------------|
| AuthenticationError | 401 |
| RateLimitError | 429 |
| APITimeoutError | 500 |
| APIConnectionError | 500 |
| APIStatusError | 实际状态码或 500 |
| 其他异常 | 500 |

### 日志粒度

| 级别 | 内容 |
|------|------|
| DEBUG | 请求/响应体、流式 chunk、SDK 事件、配置详情、流式请求 body、流式完成确认 |
| INFO | 生命周期事件、请求发送、响应接收、server 启动/停止、流式响应完成 |

敏感信息（API key）在日志中掩码为 `***`。

**流式请求日志一致性**：

两个适配器的流式处理遵循统一的日志模式：
- `_stream_request`：DEBUG 级别记录完整请求 body（与非流式请求一致）
- Server `_handle_streaming`：DEBUG 级别记录 "SSE stream completed successfully"，INFO 级别记录 "Streaming response completed"

### CLI 安全规范

所有 CLI 入口在 `__call__` 开始时调用 `mask_sensitive_args(["api_key"])`，将敏感值从进程标题中隐藏。

### Server 路由一致

两个 server 配置相同的路由：
- `POST /v1/chat/completions` — 处理 chat completions 请求
- `* /v1/{path:.*}` — 其他请求返回 404

## 扩展指南

添加新 LLM 提供商适配器时：

1. 创建 `src/psi_agent/ai/<provider_name>/` 目录
2. 实现以下文件：
   - `config.py` — 配置 dataclass，包含 session_socket、model、api_key、base_url
   - `client.py` — Async context manager client，实现核心 API 调用方法
   - `server.py` — HTTP server（Unix socket），路由 `/v1/chat/completions`
   - `cli.py` — tyro CLI 入口，调用 `mask_sensitive_args(["api_key"])`
   - `__init__.py` — 导出 Client, Server, Config
3. 对外接口必须使用 OpenAI chat completions 格式
4. 遵循统一的错误处理和日志模式
5. 编写完整测试覆盖（config、client、server、cli）
6. 在 `src/psi_agent/ai/__init__.py` 的 Commands dataclass 中添加新子命令

## 相关文档

- [openai-completions 适配器](openai_completions/CLAUDE.md)
- [anthropic-messages 适配器](anthropic_messages/CLAUDE.md)