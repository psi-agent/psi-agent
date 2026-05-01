## Why

Two issues with the current implementation:

1. **Inconsistent placeholder timing**: The "..." placeholder is sent immediately after receiving a user message, before any content arrives from the LLM. The unified principle should be: display "xxx..." only when upstream content has been received but streaming is incomplete.

2. **Typing indicator gap after message send**: When the first message is sent via `reply_text()`, Telegram automatically cancels the typing indicator. The periodic typing task waits 4 seconds before sending the next one, creating a visible gap where users see no typing indicator.

## What Changes

- Remove immediate placeholder message send after user message received
- Send first message only when the first chunk arrives from streaming response
- **Re-send typing indicator immediately after sending a message** (because Telegram cancels it on message send)
- Unified logic: all message displays follow the same pattern — content received + "..." suffix

## Capabilities

### Modified Capabilities

- `telegram-streaming-output`: Change first message timing from "immediately after user message" to "when first chunk arrives"
- `telegram-typing-indicator`: Re-send typing indicator after each message send to maintain continuous feedback

## Impact

- `src/psi_agent/channel/telegram/bot.py` — `_handle_message_streaming()` and `flush_buffer()` methods
- Tests in `tests/channel/telegram/test_bot_streaming.py`