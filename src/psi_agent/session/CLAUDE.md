# psi_agent.session

psi-session 是 psi-agent 的核心编排组件，负责消息处理、工具执行、工作区管理和定时任务调度。

## 架构概述

psi-session 位于 psi-channel（消息输入）和 psi-ai（LLM 提供商）之间，作为 agent 的运行循环核心。

```
psi-channel (client)
    │
    │ POST /v1/chat/completions (OpenAI format, HTTP over Unix socket)
    │
    ▼
psi-session (server)
    │
    │ POST /v1/chat/completions (OpenAI format, HTTP over Unix socket)
    │
    ▼
psi-ai-* (server)
    │
    │ Provider-specific API
    │
    ▼
LLM Provider
```

### 核心职责

| 职责 | 说明 |
|------|------|
| 消息处理 | 接收 channel 请求，调用 LLM，处理 tool calls，返回响应 |
| 工具执行 | 从 workspace 动态加载工具，并行执行 tool calls |
| 工作区热重载 | 检测 workspace 文件变更，动态更新工具、技能、定时任务 |
| 定时任务 | 基于 cron 表达式执行定时任务 |
| 历史持久化 | 可选的对话历史持久化到 JSON 文件 |

### 通信协议

- **与 channel**：HTTP over Unix socket，session 作为 server
- **与 psi-ai**：HTTP over Unix socket，session 作为 client
- **请求/响应格式**：OpenAI chat completions API 格式
- **流式响应**：SSE (Server-Sent Events)

## 模块结构

```
src/psi_agent/session/
├── __init__.py          # 公共导出：Session, SessionConfig, SessionRunner, SessionServer, types
├── config.py            # SessionConfig dataclass
├── types.py             # 核心数据结构：ToolSchema, ToolRegistry, History
├── server.py            # HTTP server，处理 channel 请求
├── runner.py            # 核心消息处理和 tool call 处理
├── tool_loader.py       # 动态工具加载
├── tool_executor.py     # 工具执行（支持并行）
├── workspace_watcher.py # 热重载变更检测
├── schedule.py          # 定时任务加载和执行
├── history.py           # 对话历史持久化
└── cli.py               # tyro CLI 入口
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `config.py` | 配置 dataclass，包含 channel_socket、ai_socket、workspace、history_file |
| `types.py` | 核心数据结构定义 |
| `server.py` | HTTP server，监听 Unix socket，路由 `/v1/chat/completions` |
| `runner.py` | 核心运行循环：消息处理、tool call 循环、流式/非流式响应；含 `_parse_streaming_response` 统一解析 SSE |
| `tool_loader.py` | 扫描 tools 目录，动态导入，解析 docstring，生成 OpenAI schema |
| `tool_executor.py` | 执行工具函数，支持并行执行多个 tool calls |
| `workspace_watcher.py` | MD5 哈希检测文件变更，生成 ChangeSummary |
| `schedule.py` | 解析 TASK.md frontmatter，cron 调度执行 |
| `history.py` | JSON 文件读写，历史初始化和持久化 |
| `cli.py` | tyro CLI 入口，创建 config 和 server |

## 核心数据结构

### ToolSchema

工具的完整定义，包含执行元数据：

```python
@dataclass
class ToolSchema:
    name: str                                    # 工具名称（来自文件名）
    schema: dict[str, Any]                       # OpenAI function schema
    func: Callable[..., Coroutine[Any, Any, Any]]  # async 工具函数
    file_hash: str                               # MD5 哈希，用于热重载检测
```

### ToolRegistry

工具注册表，管理所有已加载的工具：

```python
@dataclass
class ToolRegistry:
    tools: dict[str, ToolSchema] = field(default_factory=dict)

    def get(self, name: str) -> ToolSchema | None    # 按名称获取
    def register(self, tool: ToolSchema) -> None     # 注册工具
    def unregister(self, name: str) -> None          # 注销工具
    def clear(self) -> None                          # 清空所有
    def list_tools(self) -> list[dict[str, Any]]     # 返回 OpenAI schema 列表
```

### History

对话历史管理：

```python
@dataclass
class History:
    messages: list[dict[str, Any]] = field(default_factory=list)
    history_file: str | None = None

    def add_message(self, message: dict[str, Any]) -> None  # 添加消息
    def clear(self) -> None                                  # 清空历史
```

## 消息处理流程

### 非流式处理

```
1. Server 接收 POST /v1/chat/completions
2. 提取最后一条 user 消息
3. 检测 workspace 变更（热重载）
4. 构建消息列表（system prompt + history）
5. 调用 psi-ai（内部使用流式）
6. 处理 tool calls 循环：
   a. 收集流式响应中的 tool_calls
   b. 如果有 tool calls：
      - 执行工具
      - 添加 assistant message + tool results 到历史
      - 继续调用 psi-ai
   c. 如果无 tool calls：结束循环
7. 返回最终响应给 channel
8. 持久化历史
```

### 流式处理

```
1-4. 同非流式
5. 调用 psi-ai 并流式转发：
   - reasoning 字段直接转发（thinking blocks）
   - content 字段直接转发
   - tool_calls 收集
6. 如果有 tool calls：
   - 执行工具
   - 将 tool info 作为 reasoning 字段 yield
   - 继续流式调用 psi-ai
7. yield "data: [DONE]"
8. 持久化历史
```

### 关键差异

| 方面 | 非流式 | 流式 |
|------|--------|------|
| 响应方式 | 完整响应 | SSE chunks |
| thinking blocks | 预置到 content | 作为 reasoning 字段流式发送 |
| tool info | 预置到 content | 作为 reasoning 字段流式发送 |
| 历史持久化 | 返回前 | 完成后 |

## 工具系统

### 发现

扫描 `workspace/tools/` 目录下的 `.py` 文件：

```python
async def scan_tools_directory(tools_dir: anyio.Path) -> dict[str, tuple[anyio.Path, str]]:
    # 返回 {tool_name: (file_path, file_hash)}
```

### 加载

动态导入并生成 OpenAI schema：

```python
async def load_tool_from_file(file_path: anyio.Path) -> ToolSchema | None:
    # 1. 动态导入模块
    # 2. 查找 `tool` 函数
    # 3. 验证是 async 函数
    # 4. 解析 Google-style docstring
    # 5. 从类型注解生成 OpenAI parameters schema
```

### 工具函数签名

```python
async def tool(arg1: str, arg2: int = 10) -> str:
    """简短描述。

    详细描述（可选）。

    Args:
        arg1: 第一个参数的描述。
        arg2: 第二个参数的描述。

    Returns:
        返回值的描述。
    """
```

### Schema 生成

Python 类型 → OpenAI 类型映射：

| Python 类型 | OpenAI 类型 |
|-------------|-------------|
| str | string |
| int | integer |
| float | number |
| bool | boolean |
| list, List | array |
| dict, Dict | object |

### 执行

并行执行多个 tool calls：

```python
async def execute_tools_parallel(
    registry: ToolRegistry,
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    # 1. 解析每个 tool call 的 arguments JSON
    # 2. 创建 asyncio tasks
    # 3. asyncio.gather 并行执行
    # 4. 返回 tool result messages
```

## 工作区热重载

### 检测时机

每次处理用户消息前调用 `watcher.check_for_changes()`。

### 检测方法

MD5 文件哈希比较：

```python
async def compute_file_hash(file_path: anyio.Path) -> str:
    content = await file_path.read_bytes()
    return hashlib.md5(content).hexdigest()
```

### 监控范围

| 目录 | 文件 | 变更响应 |
|------|------|----------|
| `tools/` | `*.py` | 更新 ToolRegistry |
| `skills/` | `*/SKILL.md` | 重建 system prompt |
| `schedules/` | `*/TASK.md` | 重建 system prompt + 更新 ScheduleExecutor |

### 不支持热重载

`systems/system.py` 修改后需要重启 session。

### ChangeSummary

```python
@dataclass
class ChangeSummary:
    tools_added: list[str]
    tools_removed: list[str]
    tools_modified: list[str]
    skills_added: list[str]
    skills_removed: list[str]
    skills_modified: list[str]
    schedules_added: list[str]
    schedules_removed: list[str]
    schedules_modified: list[str]

    @property
    def has_changes(self) -> bool: ...
```

## 定时任务系统

### 任务格式

`workspace/schedules/<name>/TASK.md`：

```markdown
---
name: daily-summary
description: Generate daily summary
cron: "0 9 * * *"
---

Task instruction content here...
```

### 必填字段

- `cron`: Cron 表达式（如 `"0 9 * * *"` 表示每天 9:00）

### 可选字段

- `name`: 任务名称（默认为目录名）
- `description`: 任务描述

### Schedule 类

```python
@dataclass
class Schedule:
    name: str
    cron: str
    content: str
    task_dir: anyio.Path
    description: str = ""

    def get_next_run(self) -> datetime: ...
    def get_seconds_until_next_run(self) -> float: ...
```

### ScheduleExecutor

```python
class ScheduleExecutor:
    def __init__(self, schedules: list[Schedule], runner: SessionRunner): ...

    async def start(self) -> None:        # 启动所有调度循环
    async def stop(self) -> None:         # 停止所有调度
    async def add_schedule(self, schedule: Schedule) -> None:      # 添加新任务
    async def remove_schedule(self, schedule_name: str) -> None:   # 移除任务
    async def update_schedule(self, schedule: Schedule) -> None:   # 更新任务
```

### 执行流程

1. 计算到下次运行的时间
2. `await asyncio.sleep(delay)`
3. 调用 `runner.process_request({"role": "user", "content": schedule.content})`
4. 循环

## 历史持久化

### 配置

```python
@dataclass
class SessionConfig:
    history_file: str | None = None  # JSON 文件路径
```

### 存储格式

```json
[
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": "Hi!"},
  {"role": "user", "content": "..."},
  ...
]
```

### 生命周期

- **启动时**：`initialize_history()` 从文件加载（如果存在）
- **每次对话后**：`persist_history()` 写入文件

### 相关函数

```python
async def initialize_history(history_file: str | None) -> History: ...
async def persist_history(history: History) -> None: ...
async def load_history_from_file(history_file: anyio.Path) -> list[dict[str, Any]]: ...
async def save_history_to_file(history: History, history_file: anyio.Path) -> None: ...
```

## System 接口

### 位置

`workspace/systems/system.py`

### System 类

```python
class System:
    def __init__(self, workspace: anyio.Path) -> None:
        self.workspace = workspace

    async def build_system_prompt(self) -> str:
        """构建 system prompt。

        扫描 skills/ 目录，提取所有 SKILL.md 的 description，
        组合成 system prompt 返回。
        """
        ...

    async def compact_history(
        self,
        messages: list[dict[str, Any]],
        complete_fn: Callable[[list[dict[str, Any]]], Awaitable[str]],
    ) -> list[dict[str, Any]]:
        """压缩对话历史。

        当历史过长时，使用 LLM 摘要压缩旧消息。
        complete_fn 是用于调用 LLM 的函数。
        """
        ...
```

### 调用时机

| 方法 | 调用时机 |
|------|----------|
| `build_system_prompt()` | 启动时、skills/schedules 变更时 |
| `compact_history()` | 每次 LLM 请求前 |

### 函数式接口（兼容）

也支持模块级函数：

```python
async def build_system_prompt() -> str: ...
async def compact_history(history: list[dict[str, str]], max_tokens: int = 4000) -> list[dict[str, str]]: ...
```

## HTTP 接口

### 端点

`POST /v1/chat/completions`

### 请求格式

```json
{
  "model": "any-model",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": false
}
```

**注意**：
- `model` 字段被忽略，实际模型由 psi-ai 决定
- 只处理最后一条 `role: user` 的消息

### 非流式响应

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hi there!"
      },
      "finish_reason": "stop"
    }
  ],
  "model": "session"
}
```

**注意**：tool calls 被过滤，channel 只收到最终消息。

### 流式响应

```
data: {"choices": [{"delta": {"reasoning": "..."}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": "Hi"}, "finish_reason": null}]}

data: {"choices": [{"delta": {"content": " there"}, "finish_reason": null}]}

data: [DONE]
```

### 错误响应

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Error: ..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

## CLI 使用

```bash
psi-agent session \
  --channel-socket ./channel.sock \
  --ai-socket ./ai.sock \
  --workspace ./workspace \
  --history-file ./history.json
```

### 参数

| 参数 | 说明 |
|------|------|
| `--channel-socket` | 与 channel 通信的 Unix socket 路径 |
| `--ai-socket` | 与 psi-ai 通信的 Unix socket 路径 |
| `--workspace` | workspace 目录路径 |
| `--history-file` | 历史持久化文件路径（可选） |

## 与其他组件的关系

- **psi-channel-\***：作为 client 调用 session 的 HTTP API
- **psi-ai-\***：session 作为 client 调用 psi-ai 的 HTTP API
- **workspace**：session 读取 tools/、skills/、schedules/、systems/ 目录
