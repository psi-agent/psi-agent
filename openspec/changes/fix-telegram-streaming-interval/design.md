## Context

The current implementation in `_handle_message_streaming` uses a time-window buffer mechanism:
1. `on_chunk` (synchronous) appends chunks to a buffer
2. `on_chunk` cancels any pending flush task and creates a new one with `asyncio.create_task(schedule_flush())`
3. `schedule_flush` waits for `stream_interval` seconds then calls `flush_buffer`

The problem is that `asyncio.create_task()` only schedules the task; it doesn't start executing immediately. The event loop must get control back for the task to run. Since `send_message_stream` iterates over the response content in a tight `async for` loop, the flush tasks never get a chance to execute until the stream ends.

## Goals / Non-Goals

**Goals:**
- Ensure flush tasks execute during streaming, not just after
- Maintain the time-window batching behavior (multiple chunks within interval are batched)
- Keep the implementation simple and maintainable
- Add proper tests for timing behavior

**Non-Goals:**
- Changing the callback interface between client and bot
- Adding complex async primitives beyond what's necessary
- Changing behavior for non-streaming mode

## Decisions

### Decision 1: Use `asyncio.sleep(0)` to yield control in `on_chunk`

**Rationale**: The simplest fix is to yield control to the event loop after scheduling the flush task. By adding `asyncio.sleep(0)` after `asyncio.create_task()`, we allow the event loop to run other tasks, including our scheduled flush.

**Problem**: `on_chunk` is a synchronous callback, so we can't use `await asyncio.sleep(0)` directly.

### Decision 2: Change `on_chunk` to be an async callback

**Rationale**: Make `on_chunk` an async coroutine that can properly yield control. The client's `send_message_stream` would then need to await the callback.

**Trade-off**: This changes the interface between client and bot, but makes the timing behavior correct.

### Decision 3: Use a background task that periodically flushes

**Rationale**: Instead of scheduling a flush on each chunk, run a background task that checks the buffer every `stream_interval` and flushes if there's content.

**Trade-off**: Simpler control flow, but slightly different behavior - flushes happen at fixed intervals regardless of chunk timing.

### Selected Approach: Decision 3 - Background periodic flush task

This approach:
1. Start a background flush task when streaming begins
2. The task loops: sleep for `stream_interval`, then flush if buffer has content
3. Stop the task when streaming ends
4. Do a final flush for any remaining content

This is simpler and more reliable because:
- No need to manage canceling and recreating tasks on each chunk
- The event loop naturally runs the background task during stream processing
- Timing is more predictable
- Less complex than Decision 2

## Risks / Trade-offs

**Risk**: The background task approach may result in slightly different timing than the "reset timer on each chunk" approach, but this is acceptable for the use case.

**Risk**: Need to ensure proper cleanup of the background task on exceptions.

**Trade-off**: Simpler code but fixed-interval flushes instead of adaptive timing based on chunk arrival.
