# Proposal: Fix Telegram Typing Indicator

## Summary

Fix issue #93: The Telegram channel currently only sends a typing indicator once before streaming starts. During long streaming responses, the typing indicator disappears after ~5 seconds (Telegram's timeout), leaving users without feedback during message generation.

## Motivation

The typing indicator is important for user experience because:
1. It provides visual feedback that the bot is "thinking" or generating a response
2. Without it, users may think the bot is unresponsive during long LLM responses
3. Telegram's typing action only lasts about 5 seconds, so it needs to be sent periodically

## Design

Add a background task that periodically sends the `ChatAction.TYPING` action during the streaming response. The task will:
1. Start when streaming begins
2. Send typing action every 4 seconds (conservative, under Telegram's ~5 second timeout)
3. Stop when streaming ends

### Implementation Details

1. Create an `asyncio.Task` that runs in the background during streaming
2. Use a `typing_interval` constant (4 seconds) to periodically send typing actions
3. The task should gracefully handle cancellation when streaming ends
4. Add error handling for typing action failures (network issues, etc.)

### Code Changes

In `src/psi_agent/channel/telegram/bot.py`:
- Add a `_typing_indicator_loop` async function that sends typing actions periodically
- Modify `_handle_message_streaming` to start/stop the typing task

## Non-goals

- Changing the non-streaming handler behavior (it already sends one typing action)
- Making the typing interval configurable (using a constant is sufficient)
- Changing how other channels handle typing indicators

## Testing

- Add unit tests to verify:
  1. Typing indicator is sent at the start of streaming
  2. Typing indicator task runs during streaming
  3. Typing indicator task is cancelled when streaming ends
  4. Typing indicator errors are handled gracefully
