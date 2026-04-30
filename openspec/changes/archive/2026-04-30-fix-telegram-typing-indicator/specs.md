# Spec: Telegram Typing Indicator Behavior

## Overview

The Telegram channel must provide continuous typing feedback during streaming responses to improve user experience.

## Requirements

### Functional Requirements

1. **FR-1**: The typing indicator must be sent at the start of every streaming response.
2. **FR-2**: The typing indicator must be sent periodically during streaming to maintain the indicator.
3. **FR-3**: The typing indicator must stop being sent when streaming completes or fails.
4. **FR-4**: The typing indicator interval must be less than Telegram's timeout (~5 seconds).

### Non-functional Requirements

1. **NFR-1**: Typing indicator failures must not affect the main streaming flow.
2. **NFR-2**: The typing task must be properly cleaned up on cancellation.
3. **NFR-3**: Debug logging must be added for typing indicator actions.

## Constants

- `TYPING_INTERVAL`: 4 seconds - interval between typing indicator sends

## Interface

The `_handle_message_streaming` function will manage a background typing task:

```python
typing_task: asyncio.Task[None] | None = None

async def send_typing_periodically() -> None:
    """Send typing action periodically until cancelled."""
    ...

# Start typing task
typing_task = asyncio.create_task(send_typing_periodically())

# ... streaming happens ...

# Cancel typing task
if typing_task is not None:
    typing_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await typing_task
```

## Error Handling

- Typing action send failures should be logged at DEBUG level
- Failures should not raise exceptions or interrupt streaming
- The typing task should catch `asyncio.CancelledError` and exit cleanly
