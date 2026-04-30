## Context

Session 组件在处理 AI 响应时，需要记录完整的响应信息以便调试和监控。当前实现只记录 `content` 字段的前 100 字符，导致思考内容、工具调用等信息不可见。

当前日志代码位于 `src/psi_agent/session/runner.py`:
- `_process_request` 方法（非流式）：第 390 行
- `_stream_conversation` 方法（流式）：第 559 行

## Goals / Non-Goals

**Goals:**
- 完整记录 AI 响应中的所有非空字段
- 包括 `content`、`tool_calls`、以及可能存在的 `reasoning_content` 等字段
- 保持 DEBUG 日志级别，不影响生产环境性能
- 遵循防御性编程规范，处理 null 值

**Non-Goals:**
- 不修改 AI 组件的日志逻辑
- 不改变日志级别或输出格式
- 不影响非 DEBUG 级别的日志

## Decisions

### 1. 日志记录策略

**决定**: 对每个 delta chunk，分别检查并记录各字段：
- `content`: 如果非空，记录完整内容（或前 500 字符摘要）
- `tool_calls`: 如果存在，记录工具调用信息（名称和参数摘要）
- 其他字段（如 `reasoning_content`）: 如果存在且非空，记录

**理由**: 分字段记录比记录整个 chunk JSON 更易读，且可以针对不同字段类型采用不同的摘要策略。

### 2. 空值处理

**决定**: 使用防御性编程模式，跳过空值字段：
- `if delta.get("field") is not None:` 检查后再记录
- 对于嵌套结构，逐层检查

**理由**: 遵循已有的防御性编程规范，避免日志代码本身导致崩溃。

## Risks / Trade-offs

- **日志量增加**: DEBUG 级别日志会增加，但这是预期的，且不影响生产环境（生产通常不启用 DEBUG）
- **敏感信息**: 如果 AI 响应包含敏感信息，会在日志中可见。这是 DEBUG 日志的固有风险，应在生产环境禁用 DEBUG
