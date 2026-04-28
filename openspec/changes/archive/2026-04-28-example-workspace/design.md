## Context

psi-agent 的 workspace 结构已在 CLAUDE.md 中定义，但缺少具体示例和 systems 接口的实现规范。需要创建一个简单但完整的 workspace 示例，包含：
- 一个 async bash tool
- 一个 hyw skill（测试 skill 懒加载机制）
- async systems/system.py 的实现

## Goals / Non-Goals

**Goals:**
- 创建 example workspace 目录结构示例
- 实现 async bash tool（使用 asyncio.create_subprocess_exec）
- 实现 hyw skill（description 仅说明何时使用，不暴露具体行为）
- 实现 async systems/system.py（async build_system_prompt, async compact_history）
- 更新 CLAUDE.md 添加 async 接口规范

**Non-Goals:**
- 不实现 psi-session（仅提供 workspace 示例）
- 不实现 schedules（此示例不包含定时任务）
- 不实现复杂的 compact_history（仅提供框架）

## Decisions

### async 接口规范

**所有接口函数必须是 async：**

- `tool()` — async，使用 `asyncio.create_subprocess_exec`
- `build_system_prompt()` — async，使用 `aiofiles` 或 `asyncio` 异步读取文件
- `compact_history()` — async，调用 LLM API

**所有 IO 操作必须使用 async 生态：**

- 文件系统：`aiofiles` 或 `asyncio` 包装
- 网络：`httpx.AsyncClient` 或 `aiohttp`
- 子进程：`asyncio.create_subprocess_exec`（不是 subprocess.run）

### async bash tool 实现

使用 `asyncio.create_subprocess_exec` 执行 shell 命令。

函数签名：
```python
async def tool(command: str, timeout: int = 30) -> str:
    """Execute a bash command asynchronously.
    
    Args:
        command: The bash command to execute.
        timeout: Timeout in seconds.
    
    Returns:
        Command output or error message.
    """
```

实现要点：
- 使用 `asyncio.create_subprocess_exec(*command.split(), ...)`
- 使用 `asyncio.wait_for(process.communicate(), timeout)` 处理超时
- 不使用 `subprocess.run`（同步阻塞）

### hyw skill 实现

SKILL.md 使用 YAML frontmatter 格式。**description 不暴露具体行为，仅说明何时使用：**

```markdown
---
name: hyw
description: Use this skill when asking the user questions.
---

Detailed instructions here...
```

这样设计是为了测试 skill 懒加载机制：
- psi-session 最初只能看到 description
- 当 agent 决定需要此 skill 时，调用阅读类 tool 查看完整内容
- agent 自己发现需要添加"何意味？"前缀

### async build_system_prompt 实现

扫描 `workspace/skills/*/SKILL.md`，使用异步 IO 解析 YAML frontmatter。

函数签名：
```python
async def build_system_prompt() -> str:
    """Build system prompt by scanning skills directory asynchronously.
    
    Returns:
        System prompt string containing skill descriptions.
    """
```

实现要点：
- 使用 `asyncio` 异步遍历目录
- 使用 `aiofiles` 异步读取文件

### async compact_history 实现

使用 LLM 摘要压缩过长历史。框架实现，后续可完善。

函数签名：
```python
async def compact_history(history: list[dict], max_tokens: int = 4000) -> list[dict]:
    """Compact conversation history using LLM summarization.
    
    Args:
        history: List of conversation messages.
        max_tokens: Maximum tokens to keep.
    
    Returns:
        Compacted history list.
    """
```

## Risks / Trade-offs

- bash tool 安全风险 → 使用 timeout 限制，不执行危险命令（生产环境需更严格限制）
- compact_history 框架实现 → 后续需要完善 LLM 摘要逻辑
- async IO 需要额外依赖 → aiofiles 需添加到 dev dependencies