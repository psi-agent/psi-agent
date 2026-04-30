## Context

The Telegram channel's streaming mechanism (`_handle_message_streaming` in `bot.py`) currently uses an interval-based trigger approach:

1. When a chunk arrives, it's added to `content_buffer`
2. If time since last edit >= `stream_interval` AND no pending edit task, schedule an edit
3. The edit task sends accumulated content and updates `last_edit_time`

**The bug**: If chunks arrive within the interval, they accumulate. But if no more chunks arrive after the interval passes, the buffer is never flushed because the trigger condition (new chunk arrival) never fires.

## Goals / Non-Goals

**Goals:**
- Guarantee that buffered content is flushed within `stream_interval` seconds after the last chunk
- Maintain the minimum update interval to avoid Telegram API rate limits
- Ensure all content is displayed to the user when streaming ends

**Non-Goals:**
- Changing the public API or configuration
- Modifying other channels (REPL, etc.)
- Optimizing for minimal API calls beyond the existing interval mechanism

## Decisions

### Decision 1: Use asyncio.create_task with anyio.sleep for time-window flush

**Rationale**: Instead of triggering flush on chunk arrival, start a background task that flushes every `stream_interval` seconds. This ensures the buffer is drained even without new chunks.

**Alternatives considered**:
- `asyncio.wait_for` with timeout: More complex to implement for repeated intervals
- `anyio.Event` with timeout: Similar complexity, less readable
- Using `asyncio.Queue` with consumer task: Overkill for this simple use case

### Decision 2: Single flush task with cancel/restart on new chunks

**Rationale**: Start a flush task when the first chunk arrives. Each new chunk cancels and restarts the task, extending the window. This ensures flush happens `stream_interval` seconds after the *last* chunk, not the first.

**Alternatives considered**:
- Fixed periodic flush (every 1s regardless): Could send empty updates, wasteful
- Flush on every chunk with debouncing: Same as current approach, has the bug

### Decision 3: Keep the final flush at stream end

**Rationale**: When streaming ends, we must flush any remaining buffered content. This is already implemented and should be preserved.

## Risks / Trade-offs

- **Task cancellation overhead**: Each chunk cancels and restarts the flush task. For very high-frequency streams, this could add overhead. Mitigation: The overhead is minimal compared to network I/O, and the interval is 1 second by default.
- **Race condition between flush task and final flush**: The final flush must wait for any pending flush task to complete. Mitigation: Use `asyncio.Task` tracking and await before final flush.
