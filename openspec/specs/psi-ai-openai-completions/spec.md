# psi-ai-openai-completions

LLM provider adapter using HTTP over Unix socket with OpenAI chat completion protocol.

## Purpose

Adapter for OpenAI-compatible LLM APIs, providing a unified interface for chat completions via HTTP over Unix socket.

## Requirements

### Requirement: 启动 HTTP server 监听 Unix socket
psi-ai-openai-completions SHALL 在启动时创建 HTTP server，监听指定的 Unix socket 路径。

#### Scenario: 正常启动
- **WHEN** 用户执行 `uv run psi-ai-openai-completions --session-socket ./ai.sock`
- **THEN** server SHALL 在 ./ai.sock 上监听 HTTP 请求

#### Scenario: socket 文件已存在
- **WHEN** 指定的 socket 文件路径已存在
- **THEN** server SHALL 删除旧文件后重新创建

### Requirement: 接收 OpenAI chat completion 请求
psi-ai-openai-completions SHALL 接收 OpenAI chat completion 格式的 POST请求。

#### Scenario: 接收非 streaming 请求
- **WHEN** session 发送 POST /v1/chat/completions 请求，body 为 OpenAI chat completion 格式，stream=false
- **THEN** server SHALL 解析请求并转发给上游 API

#### Scenario: 接收 streaming 请求
- **WHEN** session 发送 POST /v1/chat/completions 请求，stream=true
- **THEN** server SHALL 解析请求并以 SSE streaming 方式转发

### Requirement: 转发请求给上游 API
psi-ai-openai-completions SHALL 将请求转发给指定的 OpenAI-compatible API。

#### Scenario: 转发到 OpenRouter
- **WHEN** 用户指定 --base-url https://openrouter.ai/api/v1 --api-key sk-or-v1-xxxxxx
- **THEN** request SHALL 被转发到 OpenRouter API

#### Scenario: 转发到本地 API
- **WHEN** 用户指定 --base-url http://localhost:8080/v1
- **THEN** request SHALL 被转发到本地 API

### Requirement: 返回响应给 psi-session
psi-ai-openai-completions SHALL 将上游 API 响应返回给 psi-session。

#### Scenario: 返回非 streaming 响应
- **WHEN** 上游 API 返回完整响应
- **THEN** server SHALL 返回 JSON 响应给 session，保持 OpenAI 格式

#### Scenario: 返回 streaming 响应
- **WHEN** 上游 API 返回 streaming 响应
- **THEN** server SHALL 以 SSE 格式返回每个 chunk 给 session

### Requirement: 支持命令行参数
psi-ai-openai-completions SHALL 支持以下命令行参数：
- --session-socket: Unix socket 路径
- --model: 使用的模型名称
- --api-key: API 密钥
- --base-url: API base URL

#### Scenario: 解析命令行参数
- **WHEN** 用户启动组件时提供参数
- **THEN** 组件 SHALL 正确解析并使用这些参数配置连接

### Requirement: 错误处理
psi-ai-openai-completions SHALL 处理基本错误情况。

#### Scenario: 上游 API 连接失败
- **WHEN** 无法连接到上游 API
- **THEN** server SHALL 返回 500 错误给 session

#### Scenario: API 认证失败
- **WHEN** 上游 API 返回 401 认证错误
- **THEN** server SHALL 返回相应错误给 session

### Requirement: 使用 loguru 日志记录
psi-ai-openai-completions SHALL 在所有关键操作处使用 loguru 进行详细日志记录。

#### Scenario: 记录请求日志
- **WHEN** server 接收到请求
- **THEN** SHALL 使用 loguru 记录请求详情（URL, method, body摘要）

#### Scenario: 记录响应日志
- **WHEN** server 发送响应
- **THEN** SHALL 使用 loguru 记录响应状态和摘要

#### Scenario: 记录错误日志
- **WHEN** 发生错误或异常
- **THEN** SHALL 使用 loguru 记录错误详情（ERROR 级别）

### Requirement: 提供 Python API
psi-ai-openai-completions SHALL 提供 Python API 供程序化调用。

#### Scenario: Python API 调用
- **WHEN** 用户通过 Python 代码调用 `psi_agent.ai.openai_completions.run(...)`
- **THEN** SHALL 正确启动 server，参数与 CLI 一致

### Requirement: 使用 tyro CLI
psi-ai-openai-completions SHALL 使用 tyro 从 Python API 自动生成 CLI。

#### Scenario: tyro CLI 封装
- **WHEN** 用户通过 CLI 启动组件
- **THEN** tyro SHALL 从 Python API 函数签名自动解析参数

### Requirement: 单元测试
psi-ai-openai-completions SHALL 提供单元测试，覆盖核心功能。

#### Scenario: 测试配置解析
- **WHEN** 运行 pytest
- **THEN** SHALL 测试配置类的参数解析功能

#### Scenario: 测试 server 功能
- **WHEN** 运行 pytest
- **THEN** SHALL 测试 server 的请求处理功能

#### Scenario: 测试 client 功能
- **WHEN** 运行 pytest
- **THEN** SHALL 测试 client 的 API 调用功能

### Requirement: OpenAI SDK client integration

The `OpenAICompletionsClient` SHALL use the official `openai` SDK's `AsyncOpenAI` client for all HTTP communication with OpenAI-compatible APIs.

#### Scenario: Non-streaming request with SDK
- **WHEN** a chat completion request is made without streaming
- **THEN** the SDK's `client.chat.completions.create()` method is called
- **AND** the response is returned as a typed object

#### Scenario: Streaming request with SDK
- **WHEN** a chat completion request is made with streaming enabled
- **THEN** the SDK's streaming API is used with `stream=True`
- **AND** chunks are yielded as SSE-formatted strings

### Requirement: SDK error handling

The client SHALL handle SDK-specific exceptions and convert them to the existing error response format.

#### Scenario: Authentication error
- **WHEN** the API returns a 401 error
- **THEN** an `AuthenticationError` exception is caught
- **AND** `{"error": "Authentication failed", "status_code": 401}` is returned

#### Scenario: Rate limit error
- **WHEN** the API returns a 429 error
- **THEN** a `RateLimitError` exception is caught
- **AND** `{"error": "Rate limit exceeded", "status_code": 429}` is returned

#### Scenario: Connection error
- **WHEN** the API is unreachable
- **THEN** an `APIConnectionError` exception is caught
- **AND** `{"error": "Connection failed", "status_code": 500}` is returned

### Requirement: Backward compatibility

The refactored client SHALL maintain identical external behavior to the current implementation.

#### Scenario: Same method signature
- **WHEN** the client is used
- **THEN** the `chat_completions(request_body, stream)` method signature remains unchanged

#### Scenario: Same response format
- **WHEN** a request completes
- **THEN** the response dict structure matches the current implementation

### Requirement: CLI masks sensitive API key from process title

The OpenAI completions CLI SHALL mask the `--api-key` argument from the process title immediately after parsing.

#### Scenario: API key masked in process title
- **WHEN** `psi-ai-openai-completions` is started with `--api-key sk-xxx`
- **THEN** the process title SHALL NOT contain `sk-xxx`
- **AND** the process title SHALL show `--api-key ***`

### Requirement: CLI imports follow Python module structure

The `psi_agent.ai.__init__.py` file SHALL import CLI classes in a way that avoids E402 lint violations.

#### Scenario: No E402 violations in ai __init__.py
- **WHEN** running `ruff check src/psi_agent/ai/__init__.py`
- **THEN** no E402 errors are reported

#### Scenario: CLI commands still work
- **WHEN** running `psi-agent ai openai-completions --help`
- **THEN** the help text is displayed correctly

#### Scenario: Anthropic messages command works
- **WHEN** running `psi-agent ai anthropic-messages --help`
- **THEN** the help text is displayed correctly