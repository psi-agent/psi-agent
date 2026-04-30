## Why

The current streaming buffer mechanism in Telegram channel has a timing bug: when messages arrive within the 1-second minimum update interval, they are accumulated but not guaranteed to be flushed. If no further messages arrive after the buffer accumulates content, the buffered messages remain stuck until the next message triggers a flush. This causes incomplete message display to users.

## What Changes

- Replace the current "interval-based trigger" mechanism with a "time-window buffer" mechanism
- Implement a buffer that flushes automatically after a fixed time window (e.g., 1 second) regardless of whether new messages arrive
- Messages arriving within the time window are accumulated and sent together when the window expires
- Ensure the final flush happens when streaming ends, capturing any remaining buffered content

## Capabilities

### New Capabilities

- `streaming-buffer-flush`: A time-window based buffer mechanism that guarantees periodic flush of accumulated streaming content

### Modified Capabilities

- None (this is an internal implementation fix, not a spec-level behavior change)

## Impact

- `src/psi_agent/channel/telegram/bot.py`: Refactor `_handle_message_streaming` method to use time-window buffer
- `src/psi_agent/channel/telegram/config.py`: No changes needed (existing `stream_interval` config applies)
