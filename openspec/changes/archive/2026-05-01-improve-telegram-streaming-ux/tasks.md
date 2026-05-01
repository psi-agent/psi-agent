## 1. Fix Typing Indicator Timing

- [x] 1.1 Modify `_send_typing_periodically()` to send typing indicator before first sleep (move sleep to end of loop)
- [x] 1.2 Add unit test verifying typing indicator is sent immediately when task starts

## 2. Implement Contextual Placeholder

- [x] 2.1 Modify `flush_buffer()` to append "..." to displayed content during streaming
- [x] 2.2 Reserve 3 characters for placeholder when truncating content
- [x] 2.3 Handle empty buffer case (show just "...")
- [x] 2.4 Ensure final message does not include "..." suffix

## 3. Testing

- [x] 3.1 Add test for typing indicator sent immediately in periodic task
- [x] 3.2 Add test for placeholder appended to buffered content
- [x] 3.3 Add test for empty buffer showing standalone "..."
- [x] 3.4 Add test for final message without placeholder suffix
- [x] 3.5 Run existing tests to ensure no regression
