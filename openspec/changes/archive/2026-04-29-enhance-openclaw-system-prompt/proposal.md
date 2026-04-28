## Why

当前 openclaw-like workspace 的 system prompt builder 仅实现了 bootstrap 文件的加载和拼接，缺少 OpenClaw system prompt 的其他重要组成部分（如身份声明、工具列表、安全原则、执行偏好等）。这些部分对于 agent 的行为指导至关重要，需要补充实现。

## What Changes

在 `examples/an-openclaw-like-workspace/` 中增强 system prompt builder：

- 添加身份声明（"You are a personal assistant running inside OpenClaw."）
- 添加 Tooling 部分（工具列表和描述）
- 添加 Tool Call Style 部分（工具调用风格指导，不含审批处理）
- 添加 Execution Bias 部分（执行偏好：行动导向、持续工作、需要证据）
- 添加 Safety 部分（安全原则）
- 添加 Workspace 部分（工作目录信息）
- 添加 Runtime 部分（host, os, arch, model, shell, Python版本）
- 添加 Skills 部分（技能加载和使用指导）
- 添加 Memory 部分（记忆系统指导）
- 添加 Heartbeats 部分（心跳处理指导）
- 添加 Silent Replies 部分（静默回复规则）
- 添加 Current Date & Time 部分（当前日期和时间信息）
- 添加 Prompt Cache Boundary 标记
- 在 schedules/ 中添加 30 分钟一次的 heartbeat 任务
- 创建 DIFF.md 描述与真实 OpenClaw 的差异

## Capabilities

### New Capabilities

- `openclaw-system-prompt-sections`: OpenClaw 风格的 system prompt 各个组成部分（身份声明、工具列表、安全原则、执行偏好、工作目录、运行时信息、技能指导、记忆指导、心跳指导、静默回复、日期时间、缓存边界）
- `heartbeat-schedule`: 30 分钟一次的 heartbeat 定时任务

### Modified Capabilities

- `openclaw-system-prompt`: 扩展现有的 system prompt builder，添加更多组成部分

## Impact

- 仅修改 `examples/an-openclaw-like-workspace/` 目录下的文件
- 不修改 `src/` 下的任何代码
- 新增 `schedules/heartbeat/` 目录和 TASK.md
- 更新 `systems/system.py` 以包含所有新增部分
