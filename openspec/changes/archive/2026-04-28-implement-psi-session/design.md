## Context

psi-session 是 psi-agent 的核心组件，需要实现：
- HTTP server（监听 Unix socket，接收 channel 请求）
- HTTP client（调用 psi-ai-* 的 Unix socket）
- Tool 动态加载和执行
- History 管理和持久化
- System prompt builder 调用

现有 psi-ai-openai-completions 提供了参考：使用 aiohttp 作为 HTTP server/client，OpenAI chat completion 协议。

## Goals / Non-Goals

**Goals:**
- 实现 session 核心运行循环
- 实现 tool 动态扫描和执行（启动时扫描 + 每次请求检查更新）
- 实现 history 内存管理 + 可选 JSON 持久化
- 实现与 channel 和 psi-ai-* 的 HTTP over Unix socket 通信
- 单元测试覆盖核心功能

**Non-Goals:**
- slash command 处理（session 只处理自然语言）
- 多用户/多会话管理（一个 session 一个对话）
- workspace systems 的具体实现（只定义调用接口）

## Decisions

### Tool 动态加载机制

**设计：**
- 启动时扫描 `workspace/tools/` 目录
- 使用 `importlib` 动态导入每个 `.py` 文件
- 解析 `tool()` 函数的类型注解和 docstring 构建 OpenAI tool schema
- 维护 `{name: (module, function, file_hash)}` registry
- 每次请求时检查目录文件 hash，如有更新重新加载

**Docstring 格式：** Google style docstring
- 函数描述作为 tool description
- Args 段解析参数描述
- Returns 段作为返回值描述

### HTTP Server/Client 实现

**选择：** 使用 aiohttp（与 psi-ai-openai-completions 保持一致）

**Server：** 监听 Unix socket，提供 `/v1/chat/completions`
- Session 作为 server，Channel 作为 client

**Client：** 连接 psi-ai-* 的 Unix socket
- Session 作为 client，psi-ai-* 作为 server

### History 管理

**设计：**
- 内存中维护 `messages: list[dict]`
- 可选 `history_file: Path | None` 参数
- 如果 `history_file` 存在：
  - 启动时从 JSON 加载
  - 每次请求后保存到 JSON
- compact_history 阈值触发机制：暂不实现，后续添加

### System Prompt Builder 调用

**设计：**
- 定义接口：`build_system_prompt() -> str`（无参数）
- 函数自己从 workspace 位置获取 tools、skills 等内容
- Session 在构建请求时调用此函数获取 system prompt
- 如果 workspace 没有 systems/system.py 或函数不存在，不包含 system prompt

### 模块结构

```
src/psi_agent/session/
├── __init__.py
├── cli.py          # tyro CLI 入口
├── config.py       # SessionConfig dataclass
├── server.py       # HTTP server (Unix socket)
├── runner.py       # 核心运行循环
├── tool_loader.py  # Tool 动态加载
├── tool_executor.py # Tool 执行
├── history.py      # History 管理
├── types.py        # 类型定义
```

## Risks / Trade-offs

- **Tool 动态加载失败** → 捕获异常，记录日志，跳过该 tool
- **History 文件损坏** → 启动时 JSON 解析失败，从空开始
- **psi-ai-* 连接失败** → 返回 OpenAI 格式错误响应给 channel
- **Tool 参数解析复杂性** → 使用 inspect + docstring parser，复杂类型可能丢失信息
- **Tool 执行无超时** → Tool 自己负责超时设计，session 无超时机制
- **Tool 无异常处理** → Tool 函数保证有返回，异常处理由 workspace 设计者负责