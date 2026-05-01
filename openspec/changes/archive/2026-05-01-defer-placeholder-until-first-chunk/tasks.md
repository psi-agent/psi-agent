## 1. Core Implementation

- [x] 1.1 Remove immediate `reply_text("...")` call after user message received
- [x] 1.2 Add `first_message_sent` flag to track whether first message has been sent
- [x] 1.3 Modify `on_chunk` callback to send first message when buffer transitions from empty to non-empty
- [x] 1.4 Handle empty response case: send "..." if no content received when streaming ends
- [x] 1.5 Re-send typing indicator after each `reply_text()` call

## 2. Testing

- [x] 2.1 Add test for first message sent on first chunk arrival
- [x] 2.2 Add test for no message sent before first chunk
- [x] 2.3 Add test for empty response fallback message
- [x] 2.4 Update existing tests that expect immediate placeholder
- [x] 2.5 Add test for typing indicator re-sent after message send
- [x] 2.6 Run all tests to ensure no regression
