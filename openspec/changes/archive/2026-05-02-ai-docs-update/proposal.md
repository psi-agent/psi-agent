## Why

PR #113 (ai-modules-review) 引入了新的日志模式和协议转换逻辑，这些变更体现了设计思路和惯例的演进。现有 CLAUDE.md 文档未记录这些设计决策和惯例，需要更新以确保文档准确反映模块的**设计思路、规范、接口、惯例**。

## What Changes

- 更新 `src/psi_agent/ai/CLAUDE.md`：记录流式请求日志惯例（与设计一致性相关）
- 更新 `src/psi_agent/ai/openai_completions/CLAUDE.md`：记录流式请求日志惯例、流式完成日志惯例
- 更新 `src/psi_agent/ai/anthropic_messages/CLAUDE.md`：记录流式请求日志惯例、流式完成日志惯例、非流式响应中 tool_use 转换的接口规范

## Capabilities

### New Capabilities

无新增能力，本次为文档更新以反映现有设计。

### Modified Capabilities

- `ai-module-documentation`: 更新 AI 模块文档的设计思路和惯例说明

## Impact

- 影响文件：`src/psi_agent/ai/CLAUDE.md`、`src/psi_agent/ai/openai_completions/CLAUDE.md`、`src/psi_agent/ai/anthropic_messages/CLAUDE.md`
- 不影响 API 或运行时行为
- 仅文档更新，无代码变更
