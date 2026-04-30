## Context

三个 channel 组件的日志风格不一致：
- **cli**: 只记录 `content` 字段，不记录 `reasoning`
- **repl**: 没有任何 stream 相关的日志
- **telegram**: 日志风格与 session 不一致

Session 的日志风格已经统一：
- 记录 `reasoning` 字段（非空时）
- 记录 `content` 字段（非空时）
- 使用 DEBUG 级别

## Goals / Non-Goals

**Goals:**
- 统一三个 channel 的日志风格，与 session 保持一致
- 记录 `reasoning` 和 `content` 字段（非空时）
- 使用相同的日志格式

**Non-Goals:**
- 不修改 channel 的业务逻辑
- 不修改 SSE 解析逻辑

## Decisions

### 1. 日志格式

**决定**: 使用与 session 相同的日志格式：
- `Stream reasoning chunk: {content}` - reasoning 字段
- `Stream content chunk: {content}` - content 字段

**理由**: 保持一致性，便于调试和监控。

### 2. 空值处理

**决定**: 只有当字段非空时才记录日志

**理由**: 避免无意义的空行日志，与 session 行为一致。

## Risks / Trade-offs

无显著风险。
