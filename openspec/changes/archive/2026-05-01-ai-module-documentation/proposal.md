## Why

psi-ai 模块包含两个 LLM 提供商适配器（openai-completions 和 anthropic-messages），它们将不同提供商的 API 转换为统一的 OpenAI chat completions 格式。随着代码演进，需要确保设计一致性、风格统一，并有充足的测试覆盖。同时，为了防止代码膨胀难以维护，需要为这三个模块编写 CLAUDE.md 文档，记录设计思路、风格和接口信息。

## What Changes

- 审查 psi-ai.openai-completions 和 psi-ai.anthropic-messages 的设计一致性
- 检查两个组件的代码风格是否统一
- 确认测试覆盖是否充足
- 创建三个 CLAUDE.md 文档：
  - `src/psi_agent/ai/CLAUDE.md` - AI 模块整体设计
  - `src/psi_agent/ai/openai_completions/CLAUDE.md` - OpenAI 适配器文档
  - `src/psi_agent/ai/anthropic_messages/CLAUDE.md` - Anthropic 适配器文档

## Capabilities

### New Capabilities

- `ai-module-documentation`: AI 模块的设计文档和架构说明

### Modified Capabilities

None - 本次变更仅添加文档，不修改现有功能。

## Impact

- `src/psi_agent/ai/` 目录结构
- 开发者理解 AI 模块的设计和接口
- 未来维护和扩展的便利性
