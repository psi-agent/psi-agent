## Why

当前的 `compact_history()` 函数只是一个简单的截断实现，保留最近的 N 条消息。OpenClaw 使用 LLM 生成摘要来压缩历史，这能更好地保留上下文信息。我们需要设计一个接口，让 workspace 的 `compact_history()` 能够使用 session 提供的 LLM 调用能力来生成摘要。

## What Changes

- 修改 `compact_history()` 函数签名，接受一个必需的 `complete_fn` 参数
- `complete_fn` 是一个单轮对话接口，session 通过它提供 LLM 调用能力
- 实现 OpenClaw 的 compaction 算法：
  - 基于 token 数量而非消息数量决定切割点
  - 从后往前遍历，累积 token 直到达到 `keep_recent_tokens` 阈值
  - 切割点可以是 user 或 assistant 消息
  - 支持 "split turn" 处理：当切割点在 assistant 消息时，生成额外的 turn prefix summary
- OpenClaw-like workspace 使用 `complete_fn` 生成对话摘要
- Simple workspace 接受但不使用 `complete_fn`，直接截断

## Capabilities

### New Capabilities

- `history-compaction`: 对话历史压缩功能，支持 LLM 摘要生成，与 OpenClaw 算法一致

### Modified Capabilities

无。

## Impact

- `examples/an-openclaw-like-workspace/systems/system.py` - 修改 `compact_history()` 函数，实现 OpenClaw compaction 算法
- `examples/a-simple-bash-only-workspace/systems/system.py` - 修改 `compact_history()` 函数签名，接受但不使用 `complete_fn`
- `src/psi_agent/session/` - Session 需要提供单轮对话接口
