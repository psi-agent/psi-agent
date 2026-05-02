## ADDED Requirements

### Requirement: AI module documentation reflects streaming logging patterns

CLAUDE.md 文档 SHALL 记录流式请求的日志惯例，确保开发者理解流式与非流式请求的日志粒度一致性。

#### Scenario: Streaming request body logging documented
- **WHEN** 开发者阅读 CLAUDE.md 文档
- **THEN** 文档 SHALL 说明 `_stream_request` 方法记录完整请求 body（DEBUG 级别）

#### Scenario: Streaming completion logging documented
- **WHEN** 开发者阅读 CLAUDE.md 文档
- **THEN** 文档 SHALL 说明 Server `_handle_streaming` 方法在流式完成后记录 DEBUG 和 INFO 两条日志

### Requirement: Anthropic translator documentation reflects tool_use conversion

CLAUDE.md 文档 SHALL 记录 `translate_anthropic_to_openai` 函数对 `tool_use` content blocks 的转换逻辑。

#### Scenario: Non-streaming tool_use conversion documented
- **WHEN** 开发者阅读 anthropic_messages/CLAUDE.md 文档
- **THEN** 文档 SHALL 说明非流式响应中 `tool_use` blocks 转换为 OpenAI `tool_calls` 格式的接口规范
