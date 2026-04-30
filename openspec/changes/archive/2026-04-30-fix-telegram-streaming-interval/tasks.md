## 1. Implementation

- [x] 1.1 Refactor `_handle_message_streaming` to use a background periodic flush task instead of per-chunk task scheduling
- [x] 1.2 The background task should loop: sleep for `stream_interval`, check buffer, flush if non-empty
- [x] 1.3 Ensure proper cleanup of background task on stream completion or error
- [x] 1.4 Keep the final flush for any remaining content after stream ends

## 2. Testing

- [x] 2.1 Add test that verifies multiple flushes happen during a long stream (not just at the end)
- [x] 2.2 Add test that verifies flushes occur at approximately `stream_interval` intervals
- [x] 2.3 Add test for edge case: stream ends before first interval (should still flush at end)
- [x] 2.4 Add test for edge case: empty stream (no content, should not crash)

## 3. Quality Assurance

- [x] 3.1 Run `uv run ruff check` to ensure lint passes
- [x] 3.2 Run `uv run ruff format` to ensure formatting is correct
- [x] 3.3 Run `uv run ty check` to ensure type checking passes
- [x] 3.4 Run `uv run pytest` to ensure all tests pass
