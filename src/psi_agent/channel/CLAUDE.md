# psi-channel

Channel 组件是 psi-agent 的消息通道层，负责连接用户界面与 psi-session。Channel 只收发最终 message，tool calling 和 thinking 局限于 session 内部。

## 架构设计

### 三层分离模式

所有 channel 子包遵循统一的三层分离架构：

| 层 | 文件 | 职责 |
|---|---|---|
| CLI 入口 | `cli.py` | tyro dataclass + `__call__`，解析命令行参数并启动运行 |
| 配置 | `config.py` | dataclass，定义配置参数和辅助方法 |
| HTTP 客户端 | `client.py` | async context manager，封装与 session 的 HTTP 通信 |

### 子包结构

```
channel/
├── __init__.py          # 统一入口，Commands dataclass 组合所有子命令
├── cli/                 # 一次性消息发送
│   ├── __init__.py
│   ├── cli.py           # Cli dataclass
│   ├── config.py        # CliConfig dataclass
│   └── client.py        # CliClient class
├── repl/                # 交互式 REPL
│   ├── __init__.py
│   ├── cli.py           # Repl dataclass
│   ├── config.py        # ReplConfig dataclass
│   ├── client.py        # ReplClient class
│   └── repl.py          # Repl 界面逻辑
└── telegram/            # Telegram Bot
    ├── __init__.py
    ├── cli.py           # Telegram dataclass
    ├── config.py        # TelegramConfig dataclass
    ├── client.py        # TelegramClient class
    └── bot.py           # TelegramBot 业务逻辑
```

### 统一入口

`__init__.py` 中的 `Commands` dataclass 使用 tyro 的 `OmitSubcommandPrefixes` 将三个子包组合为子命令：

```python
@dataclass
class Commands:
    subcommand: Annotated[Cli | Repl | Telegram, OmitSubcommandPrefixes]
```

## 与 session 的通信协议

- **协议**: HTTP over Unix socket
- **API**: OpenAI chat completion 格式 (`POST /v1/chat/completions`)
- **请求体**:
  ```json
  {
    "model": "session",
    "messages": [{"role": "user", "content": "..."}],
    "stream": true/false
  }
  ```
- **响应**: 非流式返回完整 JSON；流式返回 SSE (`data: {...}\n`)

## HTTP 客户端模式

所有 Client 类遵循相同的 async context manager 模式：

```python
async with client:
    result = await client.send_message("Hello")
```

- `__aenter__`: 创建 `aiohttp.UnixConnector` 和 `aiohttp.ClientSession`
- `__aexit__`: 关闭 session 和 connector，设为 `None`，记录日志
- `send_message()`: 统一入口，根据 config.stream 分发到流式/非流式方法

## 日志规范

| 级别 | 内容 |
|---|---|
| INFO | 组件启动 (`Starting psi-channel-<name>`) |
| DEBUG | 请求体、响应体、流式 chunk、连接初始化/关闭 |
| WARNING | session 返回空 choices |
| ERROR | 连接失败、请求失败、超时、HTTP 错误状态 |

## 错误处理

所有错误返回 `f"Error: <description>"` 格式的字符串，不抛出异常：

| 错误类型 | 返回值 |
|---|---|
| 连接失败 | `Error: Failed to connect to session at {socket_path}` |
| HTTP 错误 | `Error: Session returned status {status_code}` |
| 请求失败 | `Error: Request failed - {e}` |
| 超时 | `Error: Request timeout` |
| 空 choices | `Error: No response from session` |

## 流式处理

SSE 流式响应的解析逻辑在所有 Client 中一致：

1. 逐行读取 `response.content`
2. 跳过空行和 `data: [DONE]`
3. 解析 `data: ` 前缀后的 JSON
4. 提取 `choices[0].delta.content` 和 `choices[0].delta.reasoning`
5. `content is not None` 时追加到缓冲区
6. `content` 非空时记录日志并调用 `on_chunk` 回调

## 模块导出

所有子包通过 `__init__.py` 导出核心类：

- `cli`: `Cli`, `CliConfig`, `CliClient`
- `repl`: `Repl`, `ReplConfig`, `ReplClient`
- `telegram`: `Telegram`, `TelegramConfig`, `TelegramClient`, `TelegramBot`
