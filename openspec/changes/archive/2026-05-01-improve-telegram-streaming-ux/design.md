## Context

The current Telegram streaming implementation has two UX issues:

1. **Typing indicator timing gap**: The `_send_typing_periodically()` function sleeps 4 seconds before sending the first typing indicator:
   ```python
   while True:
       await asyncio.sleep(TYPING_INTERVAL)  # Sleeps FIRST
       await chat.send_action(ChatAction.TYPING)
   ```
   This creates a gap: initial typing sent → placeholder "..." sent → typing expires (~5s) → 4s later periodic task sends typing → typing reappears. Users see a ~4 second window with no typing indicator.

2. **Placeholder lacks context**: The "..." placeholder is sent as a standalone message, making it unclear what's being generated. When content starts arriving, the message suddenly changes from "..." to actual content.

## Goals / Non-Goals

**Goals:**
- Eliminate the typing indicator gap by sending immediately in the periodic task
- Make placeholder contextual by appending "..." to any buffered content

**Non-Goals:**
- Changing typing indicator interval (4 seconds is fine)
- Changing non-streaming behavior
- Making placeholder configurable

## Decisions

### Decision 1: Send typing immediately in periodic task

**Change**: Move the `await asyncio.sleep(TYPING_INTERVAL)` to the END of the loop, not the beginning.

**Before**:
```python
while True:
    await asyncio.sleep(TYPING_INTERVAL)  # Sleep first
    await chat.send_action(ChatAction.TYPING)
```

**After**:
```python
while True:
    await chat.send_action(ChatAction.TYPING)  # Send first
    await asyncio.sleep(TYPING_INTERVAL)  # Then sleep
```

**Rationale**: The initial typing indicator is sent before starting the task. With sleep at the end, the task immediately sends another typing (redundant but harmless), then sleeps. This ensures continuous coverage without gaps.

**Alternative considered**: Send initial typing, then start task that sleeps first. Rejected because it creates the gap we're trying to fix.

### Decision 2: Append placeholder to buffered content

**Change**: When flushing buffer during streaming, append "..." to indicate more content is coming.

**Before**:
```python
display_content = current_content[:TELEGRAM_MAX_MESSAGE_LENGTH]
```

**After**:
```python
# Reserve space for placeholder
max_content = TELEGRAM_MAX_MESSAGE_LENGTH - 3  # 3 chars for "..."
truncated = current_content[:max_content]
display_content = truncated + "..."
```

**Rationale**: Users see actual content being generated + indicator that more is coming. This provides context and matches common UX patterns (like GitHub's "Loading more..." in PR diffs).

**Edge case**: When buffer is empty (no content yet), show just "..." as before.

**Alternative considered**: Show "Generating..." at start. Rejected because it doesn't show partial progress.

## Risks / Trade-offs

- **Redundant typing indicator**: The periodic task sends typing immediately after the initial one. This is harmless (Telegram deduplicates) but adds one extra API call. Trade-off: simpler logic vs. one extra call. Acceptable.

- **Placeholder truncation**: Appending "..." reduces max content by 3 chars. Trade-off: slightly less content visible vs. better UX. Acceptable.

- **API rate limits**: Typing indicator every 4s is well within Telegram's limits. No risk.
