## 1. Core Implementation

- [x] 1.1 Refactor `_handle_message_streaming` to use time-window buffer mechanism
- [x] 1.2 Implement flush task that triggers after `stream_interval` seconds
- [x] 1.3 Add task cancellation and restart logic on new chunk arrival
- [x] 1.4 Ensure final flush waits for pending flush task before sending remaining content

## 2. Testing

- [x] 2.1 Add unit tests for time-window buffer flush behavior
- [x] 2.2 Add test for buffer flush when no new chunks arrive
- [x] 2.3 Add test for timer reset on new chunk arrival
- [x] 2.4 Add test for final flush on stream end

## 3. Quality Assurance

- [x] 3.1 Run `ruff check` and fix any lint issues
- [x] 3.2 Run `ruff format` to ensure code formatting
- [x] 3.3 Run `ty check` to verify type annotations
- [x] 3.4 Run `pytest` to ensure all tests pass
