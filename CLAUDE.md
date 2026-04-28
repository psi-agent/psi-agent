# psi-agent

psi-agent 是一个以**可移植性**和**组件化**为核心理念的 agent 框架。

## 核心理念

**可移植性**：用户只需复制 workspace 目录本身，即可完成 agent 的移植。

**组件化**：agent 由独立组件拼装而成，各组件通过 Unix socket 进行 IPC 通信，确保松耦合。

## 组件架构

psi-agent 分为四类组件：

| 组件类型 | 命名模式 | 职责 |
|---------|---------|------|
| psi-ai-* | `psi-ai-<provider>` | LLM 提供商适配，封装不同提供商接口 |
| psi-session | `psi-session` | Agent 运行循环，处理消息和 tool/skill 调用 |
| psi-channel-* | `psi-channel-<platform>` | 消息通道，连接具体平台（telegram, feishu, TUI 等） |
| psi-workspace-* | `psi-workspace-<mode>` | Workspace 打包/挂载管理 |

### psi-ai-* 组件

LLM 调用桥梁，封装不同提供商（openai-completion, anthropic-messages 等）。

职责：
- 监听 session 发来的 AI 请求
- 转发请求给底层 LLM 提供商
- 返回 LLM 响应给 session

接口：
- 协议：HTTP over Unix socket
- API 标准：OpenAI chat completion 格式
- session 作为 client，psi-ai-* 作为 server

### psi-session 组件

Agent 核心运行循环。

职责：
- 从 channel 接收用户消息
- 调用 psi-ai-* 进行思考
- 根据 workspace 中定义的 tools 执行动作
- 输出最终回复给 channel

Agent 流程：
- 用户消息直接传给 LLM
- tools 通过 API tools 字段传递给 LLM
- skills 的 description 放在 system prompt 中
- LLM 可调用阅读类 tool 查看 skill 详情

接口：
- 与 channel：HTTP over Unix socket，OpenAI chat completion 协议
- 与 psi-ai-*：HTTP over Unix socket，OpenAI chat completion 协议
- channel 只收发最终 message，tool calling 和 thinking 局限于 session 内部

### psi-channel-* 组件

消息通道适配器，连接具体平台。

职责：
- 将用户输入转发给 session
- 将 session 输出发送到平台

示例：psi-channel-tui（终端界面）、psi-channel-telegram、psi-channel-feishu

接口：
- 协议：HTTP over Unix socket
- session 作为 server，channel 作为 client
- 只传递最终 message，不暴露 tool calling 过程

### psi-workspace-* 组件

Workspace 管理器。

职责：
- 将 workspace 打包成 squashfs 或 overlayfs
- 管理挂载

**注意：具体设计待定，未来有新信息时需在此更新。**

## Workspace 结构

workspace 目录定义了一个 agent 的所有信息。用户只需复制此目录即可完成移植。

```
workspace/
|- tools/
|  |- *.py
|- skills/
|  |- */SKILL.md
|- schedules/
|  |- */TASK.md
|- systems/
   |- system.py
```

### tools/ 目录

每个 `.py` 文件定义一个 tool。

**规范：**
- 文件名：`<tool_name>.py`（如 `read.py`）
- 入口函数：`async def tool(...) -> ...`（必须是 async）
- 函数签名：使用类型注解和默认值定义参数
- 文档字符串：使用统一格式描述函数作用、参数含义、返回值含义
- session 启动时扫描 tools/ 目录并加载

**示例：**

```python
# tools/read.py

async def tool(file_path: str) -> str:
    """Read file content asynchronously.
    
    Args:
        file_path: Path to the file to read.
    
    Returns:
        File content as string.
    """
    # 使用 aiofiles 异步读取
    async with aiofiles.open(file_path) as f:
        return await f.read()
```

传递给 psi-ai-* 时使用 OpenAI tool call 规范。

### skills/ 目录

每个子目录定义一个 skill，遵循 Claude Code 习惯。

**规范：**
- 目录结构：`skills/<skill_name>/`
- 入口文件：`SKILL.md`
- meta 信息：使用 YAML frontmatter 格式

**SKILL.md 示例：**

```markdown
---
name: example-skill
description: A brief description of what this skill does.
---

Skill instructions here...
```

- session 启动时扫描 skills/ 目录
- skills 的 description 放入 system prompt
- LLM 可调用阅读类 tool 查看 skill 详情

### schedules/ 目录

定时任务定义。

**规范：**
- 目录结构：`schedules/<task_name>/`
- 入口文件：`TASK.md`
- meta 信息：使用 YAML frontmatter，包含 `cron` 字段

**TASK.md 示例：**

```markdown
---
name: daily-summary
description: Generate daily summary
cron: "0 9 * * *"  # 9am daily
---

Task instructions here...
```

**注意：记忆系统不内置实现，用户可在 workspace 中自行实现（通过 schedule + system prompt 特殊处理）。**

### systems/ 目录

系统配置。

**规范：**
- 文件：`systems/system.py`
- 必要函数：
  - `build_system_prompt()` — 构造系统 prompt
  - `compact_history()` — 对过长上下文进行压缩

**注意：具体接口待定，未来有新信息时需在此更新。**

## 编码规范

### Python 版本

使用 Python 3.14 或更高版本，尽可能使用现代特性。

### 代码风格

- 类型注解：所有函数必须使用类型注解
- 命名约定：
  - 函数/变量：snake_case
  - 类：PascalCase
  - 常量：UPPER_SNAKE_CASE
- 工具：
  - `ruff check` — lint
  - `ruff format` — format
  - `ty check` — typing 检查
- 质量检查：所有代码必须通过 format、lint、typing 和 test 才算完成

### Async 接口规范

**所有接口函数必须是 async：**

- workspace 中的 `tool()` 函数 — 必须是 async
- `build_system_prompt()` — 必须是 async
- `compact_history()` — 必须是 async

**所有 IO 操作必须使用 async 生态方法：**

- **文件系统**：使用 `aiofiles` 或 asyncio 包装
- **网络请求**：使用 `httpx.AsyncClient` 或 `aiohttp`
- **子进程**：使用 `asyncio.create_subprocess_exec` 或 `asyncio.create_subprocess_shell`（不是 `subprocess.run`）

示例：

```python
# 正确 ✓ - async tool
async def tool(command: str, timeout: int = 30) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=timeout,
    )
    ...

# 错误 ✗ - 同步 subprocess
def tool(command: str) -> str:
    result = subprocess.run(command, ...)  # 阻塞!
```

### Import 顺序规范

import 语句按以下顺序排列，每组内按字母排序：

1. **stdlib**：Python 标准库模块
2. **third-party**：第三方库（如 httpx, loguru）
3. **local**：本项目内部模块

示例：

```python
# stdlib
import json
from collections.abc import AsyncGenerator
from typing import Any

# third-party
import httpx
from loguru import logger

# local
from psi_agent.ai.openai_completions.config import OpenAICompletionsConfig
```

此规范符合 ruff isort（`I` 规则）。

### 类型注解规范

使用 Python 3.14+ 现代语法：

- **可选类型**：使用 `X | None` 而非 `Optional[X]`
- **联合类型**：使用 `X | Y` 而非 `Union[X, Y]`
- **泛型**：使用 `list[X]`, `dict[K, V]` 而非 `List[X], Dict[K, V]`

示例：

```python
# 正确 ✓
def func(data: dict[str, Any] | None) -> list[str]:
    ...

# 错误 ✗
from typing import Optional, List, Dict, Union

def func(data: Optional[Dict[str, Any]]) -> List[str]:
    ...
```

### 文档字符串规范

使用 **Google style docstring** 格式。

**函数文档字符串：**

```python
def function(arg1: str, arg2: int) -> bool:
    """简短描述（一行）。

    详细描述（可选，多行）。

    Args:
        arg1: 第一个参数的描述。
        arg2: 第二个参数的描述。

    Returns:
        返回值的描述。

    Raises:
        ValueError: 可能抛出的异常描述。
    """
```

**模块文档字符串：**

```python
"""模块简短描述。

可选的详细描述。
"""
```

**类文档字符串：**

```python
class MyClass:
    """类简短描述。

    详细描述（可选）。

    Attributes:
        attr1: 属性描述。
    """
```

### Async 上下文管理器规范

实现 `__aenter__` 和 `__aexit__` 时：

- `__aenter__`：初始化资源，返回 self
- `__aexit__`：关闭资源，将资源变量设为 `None`，记录日志

示例：

```python
class MyClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> MyClient:
        self._client = httpx.AsyncClient()
        logger.debug("Initialized client")
        return self

    async def __aexit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("Closed client")
```

### 错误处理规范

处理可能失败的异步操作（如网络请求）：

- 使用 `try-except` 捕获异常
- 使用 `loguru` 记录错误（ERROR 级别）
- 返回包含 `error` 和 `status_code` 的 dict

示例：

```python
async def request(url: str) -> dict[str, Any]:
    try:
        response = await self._client.post(url)
        if response.status_code != 200:
            logger.error(f"Request failed: {response.status_code}")
            return {"error": response.text, "status_code": response.status_code}
        return response.json()
    except httpx.ConnectError as e:
        logger.error(f"Connection failed: {e}")
        return {"error": "Connection failed", "status_code": 500}
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout: {e}")
        return {"error": "Request timeout", "status_code": 500}
```

### 日志规范

- 使用 **loguru** 进行日志记录
- 在所有关键操作处添加日志：
  - 函数入口/出口
  - 请求接收/转发/响应
  - 错误和异常
  - 配置加载
- 日志级别使用：
  - `DEBUG`：详细调试信息（请求body、响应内容等）
  - `INFO`：正常操作信息（启动、请求接收、连接建立等）
  - `WARNING`：可恢复的问题
  - `ERROR`：错误和异常

### CLI 规范

- 使用 **tyro** 实现所有命令行接口
- tyro 应该是 Python API 的直接封装：
  - 先定义 Python API 函数（带完整类型注解）
  - 使用 `tyro.cli()` 从函数签名自动生成 CLI
  - 保持 Python API 和 CLI 完全一致
- 示例：

```python
# Python API
def run(
    session_socket: str,
    model: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
) -> None:
    """Run the OpenAI completions server."""
    ...

# CLI 入口
def main() -> None:
    tyro.cli(run)
```

### 测试规范

- 所有 Python API 必须编写单元测试
- 测试放在 `tests/` 目录，结构与 `src/` 对应
- 使用 pytest 作为测试框架
- 测试覆盖：
  - 配置解析
  - API 请求/响应
  - 错误处理
  - 核心逻辑

### Package 结构

- 包名：`psi-agent`
- 源码目录：`src/psi_agent/`
- 子包结构：
  - `psi_agent.ai.*` — psi-ai-* 组件
  - `psi_agent.session` — psi-session 组件
  - `psi_agent.channel.*` — psi-channel-* 组件
  - `psi_agent.workspace.*` — psi-workspace-* 组件

### tool 函数规范

workspace 中 tools 目录下的工具函数规范：

- 入口函数名：`tool`（必须是 async）
- 使用类型注解定义参数类型
- 使用默认值定义可选参数
- 文档字符串描述函数、参数、返回值（Google style）

示例：

```python
# tools/read.py

async def tool(file_path: str) -> str:
    """Read file content asynchronously.

    Args:
        file_path: Path to the file to read.

    Returns:
        File content as string.
    """
    async with aiofiles.open(file_path) as f:
        return await f.read()
```

## 开发工作流

### 包管理

使用 `uv` 管理 Python 包。

### 启动命令示例

启动 session：

```bash
uv run psi-session \
  --workspace ./workspace \
  --channel-socket ./channel.sock \
  --ai-socket ./ai.sock
```

启动 AI 组件（OpenRouter 示例）：

```bash
uv run psi-ai-openai-completions \
  --session-socket ./ai.sock \
  --model tencent/hy3-preview:free \
  --api-key sk-or-v1-xxxxxx \
  --base-url https://openrouter.ai/api/v1
```

启动 channel（TUI 示例）：

```bash
uv run psi-channel-tui \
  --session-socket ./channel.sock
```