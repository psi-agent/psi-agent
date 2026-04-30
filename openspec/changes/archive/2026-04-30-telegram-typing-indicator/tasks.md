## 1. Core Implementation

- [x] 1.1 Add typing indicator in `_handle_message_streaming` method before sending initial placeholder message
- [x] 1.2 Import `ChatAction` from `telegram` module for typing action constant

## 2. Testing

- [x] 2.1 Add unit test for typing indicator being sent in streaming mode
- [x] 2.2 Add unit test verifying typing indicator is NOT sent in non-streaming mode
- [x] 2.3 Run all tests to ensure no regressions

## 3. Code Quality

- [x] 3.1 Run `ruff check` and fix any lint issues
- [x] 3.2 Run `ruff format` to ensure code formatting
- [x] 3.3 Run `ty check` to verify type checking passes