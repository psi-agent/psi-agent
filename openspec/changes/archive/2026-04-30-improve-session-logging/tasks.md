## 1. Session Runner Logging

- [x] 1.1 Update `_process_request` method logging to log complete content without truncation
- [x] 1.2 Update `_process_request` method to log tool_calls information when present
- [x] 1.3 Update `_stream_conversation` method logging to log complete content without truncation
- [x] 1.4 Update `_stream_conversation` method to log tool_calls information when present
- [x] 1.5 Add defensive null checks for all logged fields

## 2. Testing and Quality

- [x] 2.1 Run existing test suite to verify no regressions
- [x] 2.2 Run `ruff check` to verify lint passes
- [x] 2.3 Run `ruff format` to verify formatting
- [x] 2.4 Run `ty check` to verify type checking passes