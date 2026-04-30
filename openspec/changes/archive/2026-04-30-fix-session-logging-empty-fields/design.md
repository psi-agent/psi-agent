## Context

当前 session 日志逻辑存在问题：
1. `content` 字段为空字符串 `""` 时仍然打印日志，产生大量无意义的空行
2. AI 返回的 `reasoning` 字段（如腾讯 hy3 模型的思考内容）没有被记录

从日志示例可以看到，AI 返回的 chunk 结构包含：
- `content`: 实际输出内容（可能为空字符串）
- `reasoning`: 思考内容（如 "友好"、"地回应" 等）
- `reasoning_details`: 详细思考信息

## Goals / Non-Goals

**Goals:**
- 只有当 `content` 非空（不是 `None` 且不是空字符串）时才记录日志
- 记录 `reasoning` 字段（如果存在且非空）
- 保持对 `tool_calls` 的日志记录

**Non-Goals:**
- 不修改 AI 组件的日志逻辑
- 不改变日志级别

## Decisions

### 1. 空字符串检查

**决定**: 使用 `if content:` 检查，这会同时排除 `None` 和空字符串

**理由**: Python 中 `if content:` 等价于 `if content is not None and content != ""`，更简洁

### 2. reasoning 字段处理

**决定**: 检查 `delta.get("reasoning")`，如果非空则记录

**理由**: 某些模型（如腾讯 hy3）使用 `reasoning` 字段返回思考内容，这是调试的重要信息

## Risks / Trade-offs

- **字段名称变化**: 不同 LLM 提供商可能使用不同的字段名表示思考内容（如 `reasoning`、`thinking`、`reasoning_content` 等）。当前只处理 `reasoning`，未来可能需要扩展。
