# psi-channel-cli

CLI channel 用于一次性发送消息到 psi-session 并输出响应，适用于脚本和自动化场景。

## 架构

遵循三层分离模式：

```
cli/
├── __init__.py    # 导出 Cli, CliConfig, CliClient
├── cli.py         # CLI 入口（Cli dataclass）
├── config.py      # 配置（CliConfig dataclass）
└── client.py      # HTTP 客户端（CliClient class）
```

## 核心类

### Cli（cli.py）

CLI 入口 dataclass，使用 tyro 自动生成命令行参数。

```python
@dataclass
class Cli:
    session_socket: str    # Unix socket 路径
    message: str           # 用户消息
    stream: bool = True    # 流式模式（默认开启）
```

**行为**：
- `__call__()`: 记录 INFO 日志，创建 config 和 client，调用 `asyncio.run()`
- `_run()`: async 方法，进入 client 上下文，发送消息，输出结果
  - 流式模式：传入 `_print_chunk` 回调，逐块打印，最后换行
  - 非流式模式：等待完整响应后打印
  - 错误响应：`sys.exit(1)`
- `_print_chunk()`: 静态方法，`print(chunk, end="", flush=True)`

### CliConfig（config.py）

配置 dataclass。

```python
@dataclass
class CliConfig:
    session_socket: str        # Unix socket 路径
    stream: bool = True        # 流式模式
```

**方法**：
- `socket_path() -> anyio.Path`: 返回 socket 路径的 `anyio.Path` 对象

### CliClient（client.py）

HTTP 客户端，async context manager。

```python
class CliClient:
    def __init__(self, config: CliConfig) -> None
    async def __aenter__(self) -> CliClient
    async def __aexit__(self, ...) -> None
    async def send_message(self, message: str, on_chunk: Callable[[str], None] | None = None) -> str
```

**内部状态**：
- `_session: aiohttp.ClientSession | None` — HTTP 会话
- `_connector: aiohttp.UnixConnector | None` — Unix socket 连接器

**上下文管理器行为**：
- `__aenter__`: 创建 `UnixConnector` 和 `ClientSession`，记录 DEBUG 日志
- `__aexit__`: 关闭 session 和 connector，设为 `None`，各记录 DEBUG 日志

**send_message() 逻辑**：
1. 检查 `_session is not None`，否则抛出 `RuntimeError`
2. 根据 `config.stream` 分发到 `_send_streaming()` 或 `_send_non_streaming()`

**请求体格式**：
```json
{
  "model": "session",
  "messages": [{"role": "user", "content": "<message>"}],
  "stream": true/false
}
```

**错误处理**（不抛异常，返回错误字符串）：
- `aiohttp.ClientConnectorError` → `Error: Failed to connect to session at {path}`
- `aiohttp.ClientError` → `Error: Request failed - {e}`
- `TimeoutError` → `Error: Request timeout`
- HTTP 非 200 → `Error: Session returned status {code}`
- 空 choices → `Error: No response from session`

## 使用示例

```bash
# 流式模式（默认）
uv run psi-agent channel cli --session-socket ./session.sock --message "Hello"

# 非流式模式
uv run psi-agent channel cli --session-socket ./session.sock --message "Hello" --no-stream

# 独立命令
uv run psi-channel-cli --session-socket ./session.sock --message "Hello"
```
