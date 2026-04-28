## Context

openclaw-like workspace 是 psi-agent 框架的一个示例实现，其 system prompt builder 参考了 OpenClaw 的设计。当前实现已经包含了大部分核心功能，但有几个细节需要调整：

1. 身份声明仍使用 "OpenClaw"，应改为 "psi-agent" 以反映实际项目
2. Skills 部分缺少速率限制指导，这在调用外部 API 时很重要
3. HEARTBEAT.md 目前和其他 bootstrap 文件一起放在 cache boundary 之前，应该放在动态部分

## Goals / Non-Goals

**Goals:**
- 将身份声明改为 psi-agent
- 添加 Skills 速率限制指导
- 实现 HEARTBEAT.md 的动态上下文处理

**Non-Goals:**
- 不修改 psi-agent 核心代码（src/）
- 不添加新的工具或技能
- 不修改现有的 bootstrap 文件内容

## Decisions

### 1. 身份声明修改

将 `_build_identity_section()` 返回的字符串从：
```
You are a personal assistant running inside OpenClaw.
```
改为：
```
You are a personal assistant running inside psi-agent.
```

### 2. Skills 速率限制指导

在 `_build_skills_section()` 中添加速率限制指导：
```
- When a skill drives external API writes, assume rate limits: prefer fewer larger writes, avoid tight one-item loops, serialize bursts when possible, and respect 429/Retry-After.
```

### 3. 动态上下文文件处理

修改 `_build_project_context_section()` 和 `build_system_prompt()`：
- 将 HEARTBEAT.md 从稳定上下文列表中移除
- 在 cache boundary 之后单独加载 HEARTBEAT.md
- 这样可以优化 prompt cache，因为 HEARTBEAT.md 可能经常变化

## Risks / Trade-offs

- **身份声明改变**：可能影响用户对项目来源的认知 → 在 DIFF.md 中说明这是预期行为
- **动态上下文处理**：增加了代码复杂度 → 但这是 OpenClaw 的最佳实践，值得实现
