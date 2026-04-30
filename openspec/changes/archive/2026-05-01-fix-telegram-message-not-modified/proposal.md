## Why

When using the Telegram channel with streaming enabled, the bot attempts to edit messages with the same content multiple times. Telegram API returns an error "Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message" when the new content is identical to the current content.

This occurs in the `_handle_message_streaming` function at multiple points:
1. During buffer flush operations (line 246)
2. When editing the final message after stream ends (lines 304 and 320)

The error is logged as ERROR level, causing noise in the logs even though this is a benign condition that should be handled gracefully.

## What Changes

- Modify `_handle_message_streaming` in `src/psi_agent/channel/telegram/bot.py` to track the last sent content
- Compare new content with last sent content before calling `edit_text`
- Skip the edit operation if content is unchanged
- Add unit tests to verify the fix handles identical content correctly

## Capabilities

### New Capabilities

None - this is a bug fix.

### Modified Capabilities

- `psi-channel-telegram`: Improved handling of message editing to avoid "Message is not modified" errors from Telegram API

## Impact

- Modified file: `src/psi_agent/channel/telegram/bot.py`
- New tests in: `tests/channel/telegram/test_bot_streaming.py`
- No API changes
- No dependency changes