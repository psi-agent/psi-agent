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
- 入口函数：`def tool(...) -> ...`
- 函数签名：使用类型注解和默认值定义参数
- 文档字符串：使用统一格式描述函数作用、参数含义、返回值含义
- session 启动时扫描 tools/ 目录并加载

**示例：**

```python
# tools/read.py

def tool(file_path: str) -> str:
    """Read file content.
    
    Args:
        file_path: Path to the file to read.
    
    Returns:
        File content as string.
    """
    ...
```

**注意：docstr 统一格式待定，未来有新信息时需在此更新。**

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

### 文档字符串

使用统一格式（待定）。基本要求：
- 描述函数作用
- 说明每个参数的类型和含义
- 说明返回值的类型和含义

### tool 函数规范

- 入口函数名：`tool`
- 使用类型注解定义参数类型
- 使用默认值定义可选参数
- 文档字符串描述函数、参数、返回值

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
uv run psi-ai-openai-completion \
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