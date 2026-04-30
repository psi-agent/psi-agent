## Problem Statement

The Telegram Bot API returns a `BadRequest: Message is not modified` error when attempting to edit a message with content that is identical to its current content. This error occurs during streaming message updates when:

1. The flush buffer mechanism sends updates at regular intervals, but the content hasn't changed since the last flush
2. The final message edit after stream completion may have the same content as the last flushed update

## Solution Design

### Approach: Track Last Sent Content

Add a variable to track the last content that was successfully sent/edited. Before any `edit_text` call, compare the new content with the last sent content and skip the edit if they are identical.

### Implementation Details

1. **Add `last_sent_content` variable** in `_handle_message_streaming`:
   - Initialize as `None`
   - Update after each successful edit

2. **Modify `flush_buffer` function**:
   - Compare `display_content` with `last_sent_content`
   - Skip edit if content is unchanged
   - Update `last_sent_content` after successful edit

3. **Modify final edit logic** (lines 297-322):
   - Before editing the final message, compare with `last_sent_content`
   - Skip edit if content is unchanged

4. **Use nonlocal declaration** in nested functions to access `last_sent_content`

### Code Changes

```python
async def _handle_message_streaming(...) -> None:
    # Buffer for accumulating content
    content_buffer: list[str] = []
    sent_message: Any = None
    flush_task: asyncio.Task[None] | None = None
    last_sent_content: str | None = None  # NEW: Track last sent content

    async def flush_buffer() -> None:
        nonlocal last_sent_content  # NEW: Allow modification
        if sent_message is None or not content_buffer:
            return

        current_content = "".join(content_buffer)
        display_content = current_content[:TELEGRAM_MAX_MESSAGE_LENGTH]

        # NEW: Skip if content unchanged
        if display_content == last_sent_content:
            return

        try:
            await sent_message.edit_text(display_content)
            last_sent_content = display_content  # NEW: Update after success
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
```

Similar changes for the final edit logic at lines 301-322.

### Benefits

1. **Eliminates noise in logs**: No more ERROR logs for benign "message not modified" conditions
2. **Reduces API calls**: Skips unnecessary edit requests to Telegram API
3. **Maintains functionality**: Message content still updates correctly when it changes

### Testing Strategy

Add unit tests to verify:
1. Edit is skipped when content is identical to last sent content
2. Edit proceeds normally when content changes
3. `last_sent_content` is correctly updated after successful edits