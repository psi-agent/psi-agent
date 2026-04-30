## 1. Code Fix

- [x] 1.1 Fix null-safety check in `_reconstruct_tool_calls` for `name` field at line 651
- [x] 1.2 Fix null-safety check in `_reconstruct_tool_calls` for `arguments` field at line 653

## 2. Testing

- [x] 2.1 Add unit test for tool calls reconstruction with null name
- [x] 2.2 Add unit test for tool calls reconstruction with null arguments
- [x] 2.3 Run existing test suite to verify no regressions

## 3. Quality Checks

- [x] 3.1 Run `ruff check` to verify lint passes
- [x] 3.2 Run `ruff format` to verify formatting
- [x] 3.3 Run `ty check` to verify type checking passes
