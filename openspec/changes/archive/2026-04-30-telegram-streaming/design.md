## Context

Telegram Bot API 支持消息编辑功能（`editMessageText`），可以利用此特性实现流式输出效果。当前 Telegram channel 仅支持非流式模式，等待 session 返回完整响应后一次性发送给用户。

流式输出的挑战：
- Telegram API 有速率限制（约 30 次/秒），高频编辑可能触发限制
- LLM 流式输出通常较快（每秒数十个 chunk），直接转发会导致过多 API 调用
- 需要缓冲机制将多个 chunk 打包，减少编辑次数

参考实现：
- REPL channel 已实现流式输出，使用 `send_message_stream()` 方法和 SSE 解析
- CLI 使用 `--no-stream` 开关控制流式模式

## Goals / Non-Goals

**Goals:**
- 实现流式消息编辑，让用户实时看到 AI 响应生成过程
- 提供可配置的最小编辑间隔，避免 Telegram API 速率限制
- 保持与 REPL channel 一致的 CLI 风格

**Non-Goals:**
- 不改变 session 或 AI 组件的流式协议
- 不实现消息删除或重新生成功能
- 不处理 markdown 渲染（Telegram 有自己的解析器）

## Decisions

### 1. 流式缓冲策略

**决定：使用时间窗口缓冲**

维护一个缓冲区，收集流式 chunk，按固定时间间隔（默认 1 秒）批量更新 Telegram 消息。

**理由：**
- 简单实现，无需复杂的启发式算法
- 用户可配置间隔，适应不同场景
- 避免速率限制问题

**替代方案：**
- 按 chunk 数量触发：难以预测合适的阈值
- 按 token 边界触发：增加复杂度，收益不明显

### 2. 消息编辑实现

**决定：使用 `python-telegram-bot` 的 `edit_text()` 方法**

在收到第一个 chunk 时发送初始消息，后续 chunk 通过编辑更新。

**理由：**
- 原生 API 支持，无需额外依赖
- 与现有代码风格一致

### 3. CLI 参数设计

**决定：与 REPL channel 保持一致**

```bash
psi-agent channel telegram --token <token> --session-socket <path> [--no-stream] [--stream-interval 1.0]
```

**理由：**
- 一致的用户体验
- `--no-stream` 是否定式开关，默认启用流式
- `--stream-interval` 使用浮点数，支持亚秒级间隔

## Risks / Trade-offs

- **Telegram API 速率限制** → 设置合理的默认间隔（1 秒），并在文档中说明
- **消息长度超过 4096 字符** → 复用现有的 `split_message()` 函数，编辑时截断或分多条
- **网络延迟导致编辑顺序错乱** → 使用 asyncio 保证顺序执行
