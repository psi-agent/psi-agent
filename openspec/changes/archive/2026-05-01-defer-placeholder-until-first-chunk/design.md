## Context

Two issues with current implementation:

1. **Placeholder timing**: Sends "..." immediately after user message, before any LLM content arrives:
   ```
   User message → Send "..." → Start streaming → First chunk arrives → Edit to "H..."
   ```
   This creates inconsistency: first message has no content, subsequent messages only show when buffer has content.

2. **Typing indicator gap**: When `reply_text()` sends a message, Telegram automatically cancels the typing indicator. The periodic typing task waits 4 seconds before next send, creating a visible gap.

## Goals / Non-Goals

**Goals:**
- Unify message display logic: all messages show content + "..." only when buffer has content
- Maintain continuous typing indicator feedback (no gaps)
- Simplify code by removing special case for first message

**Non-Goals:**
- Changing typing indicator interval
- Changing how content is flushed during streaming
- Changing non-streaming behavior

## Decisions

### Decision 1: Send first message on first chunk, not on user message

**Change**: Move message send from "after user message received" to "when first chunk arrives".

**Implementation**:
- In `flush_buffer`: if `sent_message` is None and buffer has content, send first message
- First message includes content + "..." suffix

**Rationale**: Unified logic — all message displays happen when content is available.

### Decision 2: Re-send typing indicator after each message send

**Problem**: When `reply_text()` is called, Telegram cancels the typing indicator. The periodic task won't send another one for 4 seconds.

**Solution**: After each `reply_text()` call, immediately send typing indicator again.

**Implementation**:
```python
# In flush_buffer, after sending first message:
sent_message = await update.message.chat.reply_text(display_content)
# Immediately re-send typing indicator (Telegram cancelled it)
await update.message.chat.send_action(ChatAction.TYPING)
```

**Rationale**: Maintains continuous typing feedback. The periodic task continues as backup.

## Risks / Trade-offs

- **Slightly delayed first message**: Users won't see "..." immediately, only typing indicator. Acceptable because typing indicator provides feedback.

- **Extra typing indicator call**: One extra API call after each message send. Acceptable for better UX.

- **Empty response handling**: If LLM returns empty response, send fallback "..." at the end.
