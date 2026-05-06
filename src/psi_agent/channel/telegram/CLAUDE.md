# psi-channel-telegram

Telegram channel 通过 Telegram Bot API 提供消息通道，支持流式输出（逐步编辑消息）和代理配置。

## 架构

遵循三层分离模式，额外包含 Bot 业务逻辑层：

```
telegram/
├── __init__.py    # 导出 Telegram, TelegramConfig, TelegramClient, TelegramBot
├── cli.py         # CLI 入口（Telegram dataclass）
├── config.py      # 配置（TelegramConfig dataclass）
├── client.py      # HTTP 客户端（TelegramClient class）
└── bot.py         # Bot 业务逻辑（TelegramBot class）
```

## 核心类

### Telegram（cli.py）

CLI 入口 dataclass。

```python
@dataclass
class Telegram:
    session_socket: str    # Unix socket 路径
    token: str             # Telegram Bot API token
    proxy: str | None = None  # SOCKS5 代理地址
    stream: bool = True    # 流式模式（默认开启）
```

**行为**：
- `__call__()`: 记录 INFO 日志（`Starting psi-channel-telegram`），创建 config 和 TelegramBot，调用 `asyncio.run()`

### TelegramConfig（config.py）

配置 dataclass。

```python
@dataclass
class TelegramConfig:
    session_socket: str        # Unix socket 路径
    token: str                 # Telegram Bot API token
    proxy: str | None = None   # SOCKS5 代理地址
    stream: bool = True        # 流式模式
```

**方法**：
- `socket_path() -> anyio.Path`: 返回 socket 路径

**代理配置**：
- `proxy` 格式：`socks5://user:pass@host:port` 或 `socks5://host:port`
- 传入 `TelegramBot` 后，在创建 `aiohttp.TCPConnector` 时通过 `aiohttp_socks.ProxyConnector` 使用

### TelegramClient（client.py）

HTTP 客户端，async context manager。结构与 ReplClient 一致。

```python
class TelegramClient:
    def __init__(self, config: TelegramConfig) -> None
    async def __aenter__(self) -> TelegramClient
    async def __aexit__(self, ...) -> None
    async def send_message(self, message: str, user_id: str, on_chunk: Callable[[str], None] | None = None) -> str
    async def send_message_stream(self, message: str, user_id: str, on_chunk: Callable[[str], None] | None = None) -> str
```

**与 ReplClient 的差异**：
- `send_message()` 和 `send_message_stream()` 额外接受 `user_id` 参数
- 请求体包含 `"user": "telegram:<user_id>"` 字段（用于 session 识别用户）
- 请求体包含 `"model": "session"` 字段

**请求体格式**：
```json
{
  "model": "session",
  "messages": [{"role": "user", "content": "<message>"}],
  "stream": true/false,
  "user": "telegram:<user_id>"
}
```

### TelegramBot（bot.py）

Telegram Bot 业务逻辑，使用 `aiohttp` 直接调用 Telegram Bot API（不使用 python-telegram-bot 库）。

```python
class TelegramBot:
    def __init__(self, config: TelegramConfig) -> None
    async def __aenter__(self) -> TelegramBot
    async def __aexit__(self, ...) -> None
    async def run(self) -> None
```

**内部状态**：
- `config: TelegramConfig`
- `client: TelegramClient` — 与 session 通信的 HTTP 客户端
- `_session: aiohttp.ClientSession | None` — 与 Telegram API 通信的 HTTP 会话
- `_connector: aiohttp.TCPConnector | None` — TCP 连接器（支持代理）

**上下文管理器行为**：
- `__aenter__`: 创建 `TCPConnector`（带代理则使用 `ProxyConnector`），创建 `ClientSession`，记录 DEBUG 日志
- `__aexit__`: 关闭 session 和 connector，设为 `None`，各记录 DEBUG 日志

**run() 行为**：
1. 调用 `get_me()` 验证 Bot token
2. 记录 INFO 日志（Bot 用户名）
3. 进入长轮询循环：
   - 调用 `get_updates()` 获取新消息
   - 处理每条文本消息：调用 `handle_message()`
   - 处理错误：记录日志，继续循环

**handle_message() 流程**：
1. 记录 INFO 日志（用户 ID、消息内容摘要）
2. 根据 `config.stream` 选择流式或非流式
3. 流式模式：
   - 发送初始空消息，获取 `message_id`
   - 定期编辑消息更新内容（节流：至少间隔 1 秒）
   - 最终编辑为完整响应
4. 非流式模式：
   - 等待完整响应后发送

**消息分割**：
- Telegram 消息限制 4096 字符
- `_split_message()` 按字符数分割，优先在换行符处分割
- 超长响应自动分割为多条消息

**Telegram API 调用**：
- `get_me()`: `GET https://api.telegram.org/bot{token}/getMe`
- `get_updates()`: `GET https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=30`
- `send_message()`: `POST https://api.telegram.org/bot{token}/sendMessage` (JSON body: `chat_id`, `text`)
- `edit_message_text()`: `POST https://api.telegram.org/bot{token}/editMessageText` (JSON body: `chat_id`, `message_id`, `text`)

**代理支持**：
- 通过 `aiohttp_socks.ProxyConnector` 实现 SOCKS5 代理
- 代理地址从 `config.proxy` 获取
- 仅影响与 Telegram API 的通信，不影响与 session 的通信（session 使用 Unix socket）

## 使用示例

```bash
# 基本启动
uv run psi-agent channel telegram \
  --session-socket ./channel.sock \
  --token "123456:ABC-DEF"

# 使用 SOCKS5 代理
uv run psi-agent channel telegram \
  --session-socket ./channel.sock \
  --token "123456:ABC-DEF" \
  --proxy "socks5://127.0.0.1:1080"

# 非流式模式
uv run psi-agent channel telegram \
  --session-socket ./channel.sock \
  --token "123456:ABC-DEF" \
  --no-stream

# 独立命令
uv run psi-channel-telegram \
  --session-socket ./channel.sock \
  --token "123456:ABC-DEF"
```