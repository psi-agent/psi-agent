## 1. Code Fix

- [x] 1.1 Fix null-safety check in `_stream_conversation` method at line 559 in `src/psi_agent/session/runner.py`

## 2. Testing

- [x] 2.1 Add unit test for streaming with null content in delta
- [x] 2.2 Add unit test for streaming with empty string content
- [x] 2.3 Run existing test suite to verify no regressions

## 3. Quality Checks

- [x] 3.1 Run `ruff check` to verify lint passes
- [x] 3.2 Run `ruff format` to verify formatting
- [x] 3.3 Run `ty check` to verify type checking passes
