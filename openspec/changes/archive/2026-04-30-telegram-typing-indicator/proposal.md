## Why

当 Telegram bot 在流式更新响应时，用户在等待期间看不到任何反馈，不知道 bot 是否正在处理。Telegram Bot API 提供了 "typing" 动作指示器，可以在 bot 正在输入时显示给用户。这能显著改善用户体验，让用户知道 bot 正在处理他们的请求。

## What Changes

- 在流式响应开始时，发送 `send_chat_action(chat_id, "typing")` 显示"正在输入"指示器
- 在流式响应结束时，自动取消 typing 指示器（Telegram 会在 5 秒后自动取消，或发送消息时取消）
- 仅在 streaming 模式下启用此功能

## Capabilities

### New Capabilities

- `telegram-typing-indicator`: 在 Telegram bot 流式响应期间显示"正在输入"指示器

### Modified Capabilities

- `telegram-streaming-output`: 扩展现有流式输出功能，在流式更新开始时发送 typing 动作

## Impact

- 受影响文件: `src/psi_agent/channel/telegram/bot.py`
- 使用 Telegram Bot API 的 `send_chat_action` 方法
- 无破坏性变更，仅增强用户体验
