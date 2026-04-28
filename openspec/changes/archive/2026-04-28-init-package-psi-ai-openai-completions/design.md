## Context

psi-agent 是一个新的 agent 框架，采用 Unix socket IPC 通信模式。当前需要建立 Python package 框架并实现第一个组件 psi_agent.ai.openai_completions，作为 psi-ai-* 组件族的第一个实现。该组件将作为 LLM 提供商适配层，供 psi-session 调用。

## Goals / Non-Goals

**Goals:**
- 建立 Python package 框架（pyproject.toml），包名 psi-agent
- 实现 psi_agent.ai.openai_completions 子包
- 提供 Python API 和 CLI 入口（tyro 封装）
- 支持 HTTP over Unix socket
- 支持 OpenAI chat completion 协议（包括 streaming）
- 支持任意 OpenAI-compatible API（通过 base_url 参数）
- 使用 loguru 进行详细日志记录
- 编写单元测试

**Non-Goals:**
- 不实现 anthropic-messages 协议（属于 psi_agent.ai.anthropic_messages）
- 不实现 psi-session 或 psi-channel-* 组件（后续 change）
- 不实现复杂的错误重试逻辑（基本错误处理即可）

## Decisions

### 目录结构

使用 src layout，包名 psi-agent，子包结构如下：

```
src/psi_agent/
|- __init__.py
|- ai/
|  |- __init__.py
|  |- openai_completions/
|     |- __init__.py      # 导出 Python API
|     |- cli.py           # tyro CLI 入口
|     |- server.py        # HTTP server 实现
|     |- client.py        # OpenAI API client
|     |- config.py        # 配置类

tests/
|- ai/
|  |- openai_completions/
|     |- test_server.py
|     |- test_client.py
|     |- test_config.py
```

### HTTP Server 选择

使用 **aiohttp**。

理由：
- 原生支持 Unix socket
- 异步高性能
- 支持 streaming response
- 成熟稳定

替代方案：
- httpx + starlette：需要额外配置 Unix socket，不如 aiohttp 直接
- Flask：同步框架，不支持 streaming 优雅处理

### OpenAI API Client 选择

使用 **httpx** 直接发送请求。

理由：
- 不需要 openai SDK 的复杂封装
- 直接控制请求/响应，便于转发
- 支持 streaming
- 异步支持好

替代方案：
- openai SDK：封装过多，转发请求需要额外处理
- requests：同步，不适合 async server

### CLI 框架选择

使用 **tyro**。

理由：
- tyro 是 Python API 的直接封装，自动从函数签名生成 CLI
- 支持类型注解，自动生成帮助信息
- 保持 Python API 和 CLI 一致性
- 符合项目"API优先"原则

替代方案：
- argparse：需要手动定义参数，与 API 分离
- click：装饰器风格，与 API 不一致

### 日志框架选择

使用 **loguru**。

理由：
- 简洁易用，一个 import 即可
- 自动添加时间、级别、模块等信息
- 支持文件输出、rotation、compression
- 支持结构化日志

替代方案：
- logging：标准库，配置复杂
- structlog：功能强大但配置繁琐

### Streaming 支持

支持 SSE（Server-Sent Events）streaming。

- 接收请求时检查 `stream` 参数
- 使用 httpx streaming 发送给上游
- 使用 aiohttp streaming 返回给 session

### pyproject.toml scripts 配置

```toml
[project.scripts]
psi-ai-openai-completions = "psi_agent.ai.openai_completions.cli:main"
```

## Risks / Trade-offs

- **Unix socket 路径冲突风险** → 使用 session_socket 参数让用户指定路径
- **上游 API 连接失败风险** → 基本错误处理，返回 500 错误
- **Streaming 解析错误风险** → SSE 格式标准化，按 OpenAI 规范处理
- **测试覆盖不足风险** → 使用 pytest 编写单元测试，覆盖核心功能