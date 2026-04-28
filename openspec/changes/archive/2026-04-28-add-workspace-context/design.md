## Context

当前 agent 不知道自己的 workspace 目录在哪里。`build_system_prompt()` 没有传递 workspace 路径信息，bash tool 也没有参数指定工作目录。

## Goals / Non-Goals

**Goals:**
- 在 system prompt 中告知 agent 其 workspace 目录路径
- 在 bash tool 中添加 `cwd` 参数用于指定命令运行目录

**Non-Goals:**
- 修改 psi-session 核心逻辑
- 添加其他 workspace 相关功能

## Decisions

### 在 system prompt 中添加 workspace 路径

**方案：** 修改 `build_system_prompt()` 接受 workspace 路径参数，并在 prompt 中声明。

**原因：**
- Agent 需要知道自己的工作目录才能正确执行文件操作
- 简单直接，无需修改 session 核心逻辑

### 在 bash tool 中添加 cwd 参数

**方案：** 添加可选的 `cwd` 参数，使用 `asyncio.create_subprocess_shell` 的 `cwd` 参数。

**原因：**
- 符合 Python subprocess 标准做法
- 向后兼容（参数可选，默认为 None）

## Risks / Trade-offs

- 无显著风险
