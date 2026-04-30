# Design: Telegram Typing Indicator Implementation

## Architecture

The typing indicator functionality will be implemented as a background asyncio task that runs concurrently with the streaming response handling.

## Component Design

### Typing Indicator Loop

```python
TYPING_INTERVAL = 4  # seconds

async def _send_typing_periodically(chat) -> None:
    """Send typing action periodically.

    Runs in a background task, sending typing indicators at regular intervals
    until cancelled. Handles errors gracefully without interrupting the task.

    Args:
        chat: The Telegram chat object to send typing actions to.
    """
    while True:
        try:
            await chat.send_action(ChatAction.TYPING)
            logger.debug("Sent typing indicator")
        except Exception as e:
            logger.debug(f"Failed to send typing indicator: {e}")
        await asyncio.sleep(TYPING_INTERVAL)
```

### Integration with `_handle_message_streaming`

The typing task lifecycle:

1. **Start**: Create task immediately after sending initial typing action
2. **Run**: Task runs concurrently with streaming (via `on_chunk` callbacks)
3. **Stop**: Cancel and await task after streaming completes

```python
async def _handle_message_streaming(...):
    # ... existing setup ...

    # Send initial typing indicator
    typing_task: asyncio.Task[None] | None = None
    try:
        await update.message.chat.send_action(ChatAction.TYPING)
        # Start periodic typing task
        typing_task = asyncio.create_task(
            _send_typing_periodically(update.message.chat)
        )
    except Exception as e:
        logger.debug(f"Failed to send typing indicator: {e}")

    # ... existing streaming logic ...

    # Cleanup: Cancel typing task
    if typing_task is not None and not typing_task.done():
        typing_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await typing_task

    # ... existing cleanup ...
```

## Task Lifecycle Diagram

```
Stream Start
    |
    v
Send initial typing action
    |
    v
Start typing_task ------> [Background Loop]
    |                         |
    |                    Send typing (every 4s)
    |                         |
    v                         v
Streaming response        [Continue loop]
    |
    v
Stream Complete
    |
    v
Cancel typing_task <----- [Cancelled]
    |
    v
Await task cleanup
    |
    v
Send final message
```

## Error Scenarios

| Scenario | Handling |
|----------|----------|
| Initial typing send fails | Log DEBUG, continue without typing task |
| Periodic typing send fails | Log DEBUG, continue loop |
| Task cancelled | Graceful exit via `CancelledError` suppression |
| Streaming fails early | Typing task cancelled in cleanup |

## Thread Safety

All operations are within a single async context, so no explicit synchronization is needed. The `typing_task` variable is local to the function scope.