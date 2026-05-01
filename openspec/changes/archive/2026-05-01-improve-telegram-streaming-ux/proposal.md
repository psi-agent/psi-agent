## Why

The current Telegram streaming UX has two issues:

1. **Typing indicator gap**: After sending the initial typing indicator, there's a gap before the periodic typing task starts (it sleeps 4 seconds first). Users see typing indicator → "..." placeholder appears → typing disappears → ~4 seconds later typing reappears. This creates a confusing UX where users think the bot stopped responding.

2. **Placeholder position**: The "..." placeholder is sent as a standalone message, but should be appended to any incomplete content being streamed, providing better context for what's being generated.

## What Changes

- Fix typing indicator timing: Start periodic typing task immediately (no initial sleep) so there's no gap between the initial indicator and the periodic one
- Move placeholder to end of incomplete content: Instead of standalone "...", append "..." to truncated streaming content when buffer has content but streaming is incomplete

## Capabilities

### New Capabilities

- `telegram-streaming-ux`: Improved user experience for Telegram streaming output with continuous typing indicator and contextual placeholder

### Modified Capabilities

- `telegram-typing-indicator`: Change from "send once then periodic with gap" to "continuous periodic typing from start"
- `telegram-streaming-output`: Change placeholder from standalone "..." to appended "..." on incomplete content

## Impact

- `src/psi_agent/channel/telegram/bot.py` — `_send_typing_periodically()` and `_handle_message_streaming()` methods
- Tests in `tests/channel/telegram/test_bot_streaming.py`
