## Context

psi-ai 模块是 psi-agent 的 LLM 提供商适配层，包含两个组件：

### openai-completions
- 直接转发 OpenAI chat completions 请求
- 使用 OpenAI SDK (`openai.AsyncOpenAI`)
- 通过 `extra_body` 支持提供商特定参数（thinking, reasoning_effort）
- 文件：client.py, server.py, config.py, cli.py

### anthropic-messages
- 将 OpenAI 格式请求转换为 Anthropic Messages 格式
- 将 Anthropic 响应转换回 OpenAI 格式
- 使用 Anthropic SDK (`anthropic.AsyncAnthropic`)
- 包含完整的协议翻译器（translator.py）
- 文件：client.py, server.py, config.py, cli.py, translator.py

### 当前状态分析

**一致性评估：**
| 方面 | openai-completions | anthropic-messages | 一致性 |
|------|-------------------|-------------------|--------|
| 配置结构 | OpenAICompletionsConfig | AnthropicMessagesConfig | ✅ 一致 |
| CLI 入口 | OpenaiCompletions dataclass | AnthropicMessages dataclass | ✅ 一致 |
| 客户端模式 | async context manager | async context manager | ✅ 一致 |
| 错误处理 | _handle_error() | _handle_error() | ✅ 一致 |
| 流式响应 | SSE chunks | SSE chunks (translated) | ✅ 一致 |
| 日志风格 | loguru DEBUG/INFO/ERROR | loguru DEBUG/INFO/ERROR | ✅ 一致 |

**测试覆盖：**
- openai-completions: 4 测试文件，覆盖 client/server/cli/config
- anthropic-messages: 5 测试文件，覆盖 client/server/cli/config/translator
- translator.py 有 43KB 的详尽测试，覆盖所有转换场景

**设计亮点：**
1. 统一的 async context manager 模式
2. 统一的错误处理返回 `{error, status_code}` 格式
3. 统一的日志粒度（DEBUG 请求体，INFO 生命周期）
4. anthropic-messages 的 translator 支持完整的双向转换

## Goals / Non-Goals

**Goals:**
- 记录 AI 模块的整体架构和设计思路
- 记录每个适配器的接口和实现细节
- 确保两个组件的设计一致性
- 为未来维护提供参考

**Non-Goals:**
- 不修改任何现有代码
- 不添加新功能
- 不改变 API 行为

## Decisions

### 1. 文档结构

每个 CLAUDE.md 包含以下部分：
- 模块概述
- 核心组件说明
- 接口定义
- 设计决策
- 与其他模块的关系

### 2. 文档位置

- `src/psi_agent/ai/CLAUDE.md` - 模块级文档，描述整体架构
- `src/psi_agent/ai/openai_completions/CLAUDE.md` - OpenAI 适配器文档
- `src/psi_agent/ai/anthropic_messages/CLAUDE.md` - Anthropic 适配器文档

### 3. 文档内容重点

重点记录：
- 统一接口格式（OpenAI chat completions）
- 协议转换逻辑（Anthropic → OpenAI）
- 配置参数说明
- 错误处理模式
- 测试策略

## Risks / Trade-offs

- **风险**: 文档可能随代码演进而过时 → 在 CLAUDE.md 中注明"最后更新日期"，并在代码审查时检查文档一致性
- **权衡**: 文档详细程度 → 保持适度详细，重点记录设计决策而非实现细节
