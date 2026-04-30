## 1. Fix Implementation

- [x] 1.1 Fix null value handling in `runner.py:_stream_conversation()` - change `if "tool_calls" in delta:` to `if delta.get("tool_calls"):`
- [x] 1.2 Review and fix any other delta field accesses that might have similar null value issues

## 2. Testing

- [x] 2.1 Add unit test for streaming delta with null `tool_calls` value
- [x] 2.2 Add unit test for streaming delta with missing `tool_calls` field
- [x] 2.3 Add unit test for streaming delta with valid `tool_calls` array
- [x] 2.4 Run all tests to verify no regression

## 3. Quality Checks

- [x] 3.1 Run `ruff check` to verify lint compliance
- [x] 3.2 Run `ruff format` to verify formatting
- [x] 3.3 Run `ty check` to verify type checking
