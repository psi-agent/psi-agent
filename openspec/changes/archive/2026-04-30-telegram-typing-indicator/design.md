## Context

当前 Telegram channel 在流式模式下处理用户消息时，会发送初始占位消息 `"..."`，然后通过编辑消息来更新内容。用户在等待期间看不到任何反馈指示 bot 正在处理。

Telegram Bot API 提供了 `send_chat_action` 方法，可以显示"正在输入"等状态指示器。这个指示器会在 5 秒后自动消失，或者在发送消息时消失。

## Goals / Non-Goals

**Goals:**
- 在流式响应开始时发送 typing 指示器
- 提供用户反馈，改善用户体验
- 保持现有流式更新逻辑不变

**Non-Goals:**
- 非 streaming 模式不需要 typing 指示器（响应足够快）
- 不需要持续发送 typing 指示器（Telegram 自动处理 5 秒超时）

## Decisions

### Decision 1: 在发送初始占位消息前发送 typing 指示器

**选择**: 在 `_handle_message_streaming` 方法中，在 `await update.message.reply_text("...")` 之前调用 `send_chat_action`。

**理由**:
- Telegram 的 typing 指示器会在发送消息时自动消失
- 在发送初始消息前发送 typing 可以覆盖从接收消息到发送第一个响应的等待时间
- 无需额外管理指示器的取消逻辑

**替代方案**:
- 持续发送 typing 指示器：增加 API 调用次数，收益有限
- 使用后台任务定期发送：复杂度高，不必要

### Decision 2: 使用 `update.message.chat_id` 作为目标

**选择**: 使用 `update.message.chat_id` 调用 `send_chat_action`。

**理由**:
- 确保指示器发送到正确的聊天
- 与现有消息回复逻辑一致

## Risks / Trade-offs

- **API 调用增加**: 每次流式响应增加一次 API 调用 → 影响极小，Telegram API 限制宽松
- **typing 指示器超时**: 如果 LLM 响应超过 5 秒，指示器会消失 → 可接受，用户已看到初始占位消息
