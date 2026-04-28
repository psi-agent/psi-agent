## Context

当前 `examples/an-openclaw-like-workspace/systems/system.py` 仅实现了 bootstrap 文件的加载和拼接。需要扩展以包含 OpenClaw system prompt 的其他重要组成部分。

所有实现都在 `examples/an-openclaw-like-workspace/` 目录下，不修改 `src/` 下的任何代码。

## Goals / Non-Goals

**Goals:**
- 实现 OpenClaw 风格的 system prompt 各组成部分
- 添加 heartbeat 定时任务
- 创建 DIFF.md 描述差异
- 保持与 OpenClaw 的行为兼容性

**Non-Goals:**
- 不修改 psi-agent 核心代码
- 不实现 OpenClaw 特定功能（CLI、自更新等）
- 不实现通道/平台相关功能
- 不实现沙箱、Provider 扩展等高级功能

## Decisions

### System Prompt 结构

**Decision:** System prompt 按以下顺序组织：

1. 身份声明
2. Tooling（工具列表）
3. Tool Call Style（工具调用风格）
4. Execution Bias（执行偏好）
5. Safety（安全原则）
6. Workspace（工作目录）
7. Skills（技能指导）
8. Memory（记忆指导）
9. Project Context（Bootstrap 文件）
10. Prompt Cache Boundary 标记
11. Heartbeats（心跳指导）
12. Silent Replies（静默回复）
13. Current Date & Time（日期时间）
14. Runtime（运行时信息）

**Rationale:** 这个顺序与 OpenClaw 保持一致，确保 prompt cache 优化有效。

### Runtime 信息获取

**Decision:** 使用 Python 标准库获取运行时信息：
- `platform.node()` 获取 host
- `platform.system()` 和 `platform.release()` 获取 os
- `platform.machine()` 获取 arch
- `sys.version` 获取 Python 版本
- `os.environ.get('SHELL', 'unknown')` 获取 shell

**Rationale:** 使用标准库，无需额外依赖。

### Heartbeat 任务

**Decision:** 在 `schedules/heartbeat/TASK.md` 中定义 30 分钟一次的定时任务，内容为读取 HEARTBEAT.md 并执行其中的任务。

**Rationale:** 与 OpenClaw 的心跳机制功能等价，但使用 psi-agent 的 schedules 机制实现。

### Tooling 信息

**Decision:** Tooling 部分硬编码当前实现的四个工具（read, write, edit, bash）及其描述。

**Rationale:** 当前 workspace 只有这四个工具，未来可以扩展为动态扫描 tools/ 目录。

## Risks / Trade-offs

### Risk: System Prompt 过长
**Risk:** 添加多个部分后，system prompt 可能变得很长，增加 token 消耗。
**Mitigation:** 使用 Prompt Cache Boundary 标记分隔稳定和动态内容，支持 prompt cache 优化。

### Risk: 与 OpenClaw 行为不完全一致
**Risk:** 由于架构差异，某些行为可能与 OpenClaw 不完全一致。
**Mitigation:** 在 DIFF.md 中明确记录差异，用户可以根据需要调整。

### Trade-off: 硬编码 vs 动态生成
**Trade-off:** Tooling 部分使用硬编码而非动态扫描。
**Acceptance:** 当前工具数量少，硬编码简单可靠。未来可以扩展为动态生成。
