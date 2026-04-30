## Context

当前 Session 在流式响应中将思考内容（reasoning + 工具调用）包装在 `<thinking>` 标签中作为 `content` 字段发送。这导致 Channel 无法区分思考内容和最终回答。

**当前 SSE 格式：**
```
data: {"choices": [{"delta": {"content": "<thinking>...</thinking>"}}]}
data: {"choices": [{"delta": {"content": "最终回答..."}}]}
```

**期望 SSE 格式：**
```
data: {"choices": [{"delta": {"reasoning": "思考内容..."}}]}
data: {"choices": [{"delta": {"content": "回答内容..."}}]}
```

**信息流动示例：**
```
AI -> Session: reasoning: 也许我应该
Session -> Channel: reasoning: 也许我应该
AI -> Session: reasoning: 用一下date这个工具
Session -> Channel: reasoning: 用一下date这个工具
AI -> Session: content: 让我用一下date
Session -> Channel: content: 让我用一下date
AI -> Session: func tool: bash call date
Session -> Channel: reasoning: [Tool: bash] Arguments: {"command": "date"} Result: ...
Session -> AI: 请求信息: 20260430 xx:xx:xx
Session -> Channel: reasoning: 20260430 xx:xx:xx
AI -> Session: reasoning: 哦，我知道了是xxxx
Session -> Channel: reasoning: 哦，我知道了是xxxx
AI -> Session: content: 现在是xxxx
Session -> Channel: content: 现在是xxxx
```

## Goals / Non-Goals

**Goals:**
- Session 在流式响应中直接转发 AI 返回的 `reasoning` 字段
- 工具调用过程作为 `reasoning` 字段发送
- `content` 字段保持原样转发（包括 tool_calls 时的 content）
- 保持向后兼容：如果 channel 不处理 `reasoning` 字段，仍能正常工作

**Non-Goals:**
- 不修改非流式响应格式
- 不修改 history 存储格式

## Decisions

### 1. SSE delta 字段结构

**决定**: 在 delta 中直接转发 AI 的 `reasoning` 字段，工具调用过程也作为 `reasoning` 发送，`content` 保持原样转发

**格式：**
```json
{"choices": [{"delta": {"reasoning": "思考内容..."}}]}
{"choices": [{"delta": {"content": "回答内容..."}}]}
```

**理由**: 
- 保持 OpenAI SSE 格式兼容性（AI 已经返回 reasoning 字段）
- `content` 保持原样，用户看到连贯的对话流
- Channel 可以根据需要处理或忽略 `reasoning` 字段

### 2. reasoning 内容来源

**决定**: reasoning 内容包括：
1. LLM 返回的 `reasoning` 字段（直接转发）
2. 工具调用过程（工具名、参数、结果）- 格式化为文本发送
3. 工具执行结果 - 作为 reasoning 发送

**理由**: 这些都是"思考过程"，应该独立于 content 发送。

## Risks / Trade-offs

- **字段命名**: 使用 `reasoning` 字段，与 AI 返回的字段名一致
- **Channel 兼容性**: 现有 channel 可能不处理 `reasoning` 字段，但这不影响基本功能
