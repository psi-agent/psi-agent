## Context

当前 Session 在流式响应处理时，`content` 为空字符串 `""` 时仍然打印日志行，产生大量无意义的空行日志。这发生在 delta 中其他字段（如 `reasoning`）非空时。

## Goals / Non-Goals

**Goals:**
- 只有当 `content` 非空（truthy）时才记录日志
- 同样适用于 `reasoning` 字段

**Non-Goals:**
- 不修改 SSE 流式响应逻辑
- 不修改其他字段的日志行为

## Decisions

### 1. 空字符串检查

**决定**: 使用 `if content:` 检查，这会同时排除 `None` 和空字符串

**理由**: Python 中 `if content:` 等价于 `if content is not None and content != ""`，更简洁

## Risks / Trade-offs

无显著风险。
