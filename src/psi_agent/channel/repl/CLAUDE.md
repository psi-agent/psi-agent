# psi-channel-repl

REPL channel 提供交互式终端界面，支持多行输入、历史导航和流式输出。

## 架构

遵循三层分离模式，额外包含界面逻辑层：

```
repl/
├── __init__.py    # 导出 Repl, ReplClient, ReplConfig
├── cli.py         # CLI 入口（Repl dataclass）
├── config.py      # 配置（ReplConfig dataclass）
├── client.py      # HTTP 客户端（ReplClient class）
└── repl.py        # REPL 界面逻辑（Repl class）
```

## 核心类

### Repl（cli.py）

CLI 入口 dataclass。

```python
@dataclass
class Repl:
    session_socket: str    # Unix socket 路径
    stream: bool = True    # 流式模式（默认开启）
```

**行为**：
- `__call__()`: 记录 INFO 日志（`Starting psi-channel-repl`），创建 config 和 ReplRunner，调用 `asyncio.run()`

### ReplConfig（config.py）

配置 dataclass。

```python
@dataclass
class ReplConfig:
    session_socket: str            # Unix socket 路径
    history_file: str | None = None  # 历史文件路径（None 时使用默认路径）
    stream: bool = True            # 流式模式
```

**方法**：
- `socket_path() -> anyio.Path`: 返回 socket 路径
- `get_history_path() -> anyio.Path`: 返回历史文件路径
  - 配置了 `history_file` 时使用配置值
  - 未配置时使用 `platformdirs.user_cache_dir("psi-agent") / "repl_history.txt"`

### ReplClient（client.py）

HTTP 客户端，async context manager。与 CliClient 结构一致，但提供独立的流式和非流式方法。

```python
class ReplClient:
    def __init__(self, config: ReplConfig) -> None
    async def __aenter__(self) -> ReplClient
    async def __aexit__(self, ...) -> None
    async def send_message(self, message: str) -> str
    async def send_message_stream(self, message: str, on_chunk: Callable[[str], None] | None = None) -> str
```

**与 CliClient 的差异**：
- 流式和非流式是独立方法（`send_message` 和 `send_message_stream`），而非统一入口分发
- 请求体包含 `"model": "session"` 字段
- 错误处理格式与 CliClient 一致

**请求体格式**：
```json
{
  "model": "session",
  "messages": [{"role": "user", "content": "<message>"}],
  "stream": true/false
}
```

### Repl（repl.py）

REPL 界面逻辑，使用 `prompt-toolkit` 实现交互式输入。

```python
class Repl:
    def __init__(self, config: ReplConfig) -> None
    async def run(self) -> None
```

**内部状态**：
- `client: ReplClient` — HTTP 客户端
- `_session: PromptSession[None] | None` — prompt-toolkit 会话

**run() 循环行为**：
1. 打印欢迎信息
2. 初始化 `PromptSession`（带 `FileHistory`）
3. 进入 `async with self.client` 上下文
4. 循环读取用户输入：
   - `> ` 提示符，多行模式（`. ` 续行）
   - Ctrl+D (EOF) → 退出
   - 空输入 → 跳过
   - 根据 `config.stream` 调用流式或非流式方法
5. Ctrl+C → 退出
6. 其他异常 → 记录日志，打印错误，继续循环

**流式输出**：响应前空行，每个 chunk 立即打印，响应后空行
**非流式输出**：响应前后空行

**输入特性**（prompt-toolkit）：
- Enter 提交
- Alt+Enter / Escape+Enter 插入换行
- 上/下箭头导航历史
- 历史持久化到文件

**辅助函数**：
- `_ensure_history_dir()`: 确保历史文件目录存在（async，使用 `anyio.Path`）

## 使用示例

```bash
# 流式模式（默认）
uv run psi-agent channel repl --session-socket ./channel.sock

# 非流式模式
uv run psi-agent channel repl --session-socket ./channel.sock --no-stream

# 独立命令
uv run psi-channel-repl --session-socket ./channel.sock
```