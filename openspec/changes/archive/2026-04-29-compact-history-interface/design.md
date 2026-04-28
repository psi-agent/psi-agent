## Context

psi-agent 的 workspace 中有 `compact_history()` 函数，用于压缩对话历史以避免超出模型的上下文窗口限制。当前实现只是简单地保留最近的 N 条消息，这会丢失早期对话的重要上下文。

OpenClaw 的实现使用 LLM 生成摘要来压缩历史：
1. 将旧消息发送给 LLM 生成摘要
2. 用摘要替换旧消息
3. 保留最近的消息不变

这需要 workspace 能够调用 LLM，但 workspace 本身不应该知道如何调用 LLM（这是 psi-ai-* 组件的职责）。

## Goals / Non-Goals

**Goals:**
- 设计一个接口，让 session 能够将 LLM 调用能力传递给 workspace
- 修改 `compact_history()` 支持使用 LLM 生成摘要
- OpenClaw-like workspace 使用 LLM 摘要，simple workspace 直接截断

**Non-Goals:**
- 不修改 psi-ai-* 组件
- 不实现复杂的分块摘要策略（OpenClaw 的高级功能）
- 不处理 tool_use/tool_result 的配对修复

## OpenClaw Compaction 机制调研

### 关于"保留所有用户输入"

**结论：OpenClaw 不保留所有用户输入。**

OpenClaw 的 `findCutPoint` 函数可以在 user 或 assistant 消息处切割（代码注释："Can cut at user OR assistant messages (never tool results)"）。用户消息和 assistant 消息都会被压缩。

### 关于"保留最近几轮会话"

**结论：OpenClaw 基于 token 数量而非轮数保留最近内容。**

核心参数：
- `keepRecentTokens`: 默认 20000 tokens，决定保留多少最近内容
- `reserveTokens`: 默认 16384 tokens，用于 prompt + LLM response

算法：
- 从后往前遍历消息，累积 token 数量
- 当累积达到 `keepRecentTokens` 时，在该位置切割
- 切割点可以是 user 或 assistant 消息

### Split Turn 处理

当切割点在 assistant 消息（而非 user 消息）时，称为 "split turn"：
- 会生成一个额外的 "turn prefix summary"
- 将该 turn 的前半部分（user request + 部分 assistant response）摘要化
- 保留后半部分（最近的 assistant response）

这是为了处理单个 turn 过长的情况。

## Decisions

### 1. 接口设计

**决定：** 使用 Callable 类型作为必需参数，命名为 `complete_fn`

```python
from collections.abc import Awaitable, Callable

CompleteFn = Callable[[list[dict[str, Any]]], Awaitable[str]]

async def compact_history(
    history: list[dict[str, Any]],
    complete_fn: CompleteFn,
    max_tokens: int = 4000,
    keep_recent_tokens: int = 2000,
) -> list[dict[str, Any]]:
    ...
```

**参数说明：**
- `complete_fn`: 单轮对话接口，用于调用 LLM
- `max_tokens`: 最大 token 限制（用于判断是否需要压缩）
- `keep_recent_tokens`: 保留的最近 token 数量（默认为 max_tokens 的一半）

**理由：**
- `complete_fn` 更准确描述其功能：单轮对话接口
- 必需参数确保 session 必须提供此能力
- workspace 决定是否使用：openclaw-like 使用它生成摘要，simple workspace 忽略它直接截断
- workspace 不需要知道 LLM 的具体实现

### 2. Token 估算

使用 OpenClaw 的 `chars / 4` 启发式方法：

```python
def _estimate_tokens(message: dict[str, Any]) -> int:
    chars = 0
    content = message.get("content", "")

    if isinstance(content, str):
        chars = len(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    chars += len(block.get("text", ""))
                elif block.get("type") == "image":
                    chars += 4800  # 估算图片为 1200 tokens

    return max(1, chars // 4)
```

### 3. 切割点算法

实现 OpenClaw 的 `findCutPoint` 逻辑：

1. 计算历史总 token 数
2. 如果未超过 `max_tokens`，直接返回原历史
3. 从后往前遍历消息，累积 token 数量
4. 当累积达到 `keep_recent_tokens` 时，记录切割点
5. 判断是否为 "split turn"（切割点在 assistant 消息）

```python
def _find_cut_point(
    history: list[dict[str, Any]],
    keep_recent_tokens: int,
) -> tuple[int, bool]:
    """Find the cut point in history.

    Returns:
        (cut_index, is_split_turn)
        - cut_index: 第一个保留的消息索引
        - is_split_turn: 是否在 turn 中间切割
    """
    accumulated = 0
    cut_index = len(history)

    for i in range(len(history) - 1, -1, -1):
        accumulated += _estimate_tokens(history[i])
        if accumulated >= keep_recent_tokens:
            cut_index = i
            break

    # 判断是否为 split turn
    is_split_turn = (
        cut_index > 0 and
        history[cut_index].get("role") == "assistant"
    )

    return cut_index, is_split_turn
```

### 4. Split Turn 处理

当切割点在 assistant 消息时：

1. 找到该 turn 的起始 user 消息
2. 生成两个摘要：
   - **History Summary**: 切割点之前的所有消息
   - **Turn Prefix Summary**: 该 turn 的前半部分（user request + 部分 assistant response）
3. 合并两个摘要

```python
def _find_turn_start(history: list[dict[str, Any]], cut_index: int) -> int:
    """Find the user message that starts the turn containing cut_index."""
    for i in range(cut_index, -1, -1):
        if history[i].get("role") == "user":
            return i
    return 0
```

### 5. 摘要提示词

参考 OpenClaw 的实现，使用结构化的摘要格式：

**History Summary Prompt:**
```
## Goal
[What is the user trying to accomplish?]

## Constraints & Preferences
- [Any constraints, preferences, or requirements mentioned by user]

## Progress
### Done
- [x] [Completed tasks/changes]

### In Progress
- [ ] [Current work]

### Blocked
- [Issues preventing progress, if any]

## Key Decisions
- **[Decision]**: [Brief rationale]

## Next Steps
1. [Ordered list of what should happen next]

## Critical Context
- [Any data, examples, or references needed to continue]
```

**Turn Prefix Summary Prompt:**
```
## Original Request
[What did the user ask for in this turn?]

## Early Progress
- [Key decisions and work done in the prefix]

## Context for Suffix
- [Information needed to understand the retained recent work]
```

### 6. Workspace 行为差异

**OpenClaw-like workspace:**
- 使用 `complete_fn` 生成摘要
- 实现 split turn 处理
- 保留最近消息不压缩

**Simple workspace:**
- 接受 `complete_fn` 参数但忽略它
- 基于 token 数量直接截断
- 不生成摘要

### 7. Session 侧的实现

Session 需要提供一个函数，该函数：
- 接收消息列表（单轮对话）
- 调用 psi-ai-* 组件
- 返回响应字符串

```python
async def create_complete_fn(ai_client) -> CompleteFn:
    async def complete(messages: list[dict]) -> str:
        # 调用 LLM
        response = await ai_client.complete(messages)
        return response.content
    return complete
```

## Risks / Trade-offs

- **摘要质量不稳定** → 使用结构化提示词
- **LLM 调用失败** → OpenClaw-like 可 fallback 到截断
- **摘要丢失细节** → 保留最近的消息不压缩，只压缩旧消息
- **Split turn 处理复杂** → 先实现基础版本，后续优化
