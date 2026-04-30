## Why

The Telegram channel's streaming message editing feature is not working as expected. When `stream_interval` is configured to 1.0 seconds, the message edits should occur approximately every 1 second during streaming. However, the current implementation batches all edits and applies them only after the stream completes, resulting in a single final update instead of incremental updates every second.

This issue negatively impacts user experience because:
1. Users don't see real-time progress during long responses
2. The "typing indicator" effect is lost
3. The intended rate-limiting protection from Telegram API is not properly utilized

## What Changes

The streaming buffer flush mechanism in `_handle_message_streaming` needs to be fixed to ensure the scheduled flush tasks actually execute during streaming, not just after the stream completes.

The root cause is that `asyncio.create_task()` schedules tasks that only run when the event loop gets control. The `send_message_stream` function consumes the stream in a tight async loop, preventing the flush tasks from executing until the stream ends.

Changes required:
1. Modify the `on_chunk` callback mechanism to yield control to the event loop
2. Ensure the flush task can execute during stream processing
3. Add tests that verify the timing behavior of streaming updates

## Capabilities

### New Capabilities
- `telegram-streaming-timing`: Ensures Telegram streaming message edits occur at the configured `stream_interval` during streaming, not just after completion.

### Modified Capabilities
- None (this is a bug fix, not a requirement change)

## Impact

- **Affected code**: `src/psi_agent/channel/telegram/bot.py` (`_handle_message_streaming` function)
- **Affected tests**: `tests/channel/telegram/test_bot_streaming.py`
- **No API changes**: The fix is internal, no external API changes
- **Dependencies**: None