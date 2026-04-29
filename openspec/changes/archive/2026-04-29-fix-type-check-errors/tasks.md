## 1. Fix response.text Type Errors

- [x] 1.1 Fix `tests/ai/openai_completions/test_server.py` - response.text type errors
- [x] 1.2 Fix `tests/session/test_server.py` - response.text type errors

## 2. Fix AsyncMock Assignment Errors

- [x] 2.1 Fix `tests/session/test_server.py` - AsyncMock assignment to process_request
- [x] 2.2 Fix `tests/session/test_server.py` - AsyncMock assignment to process_streaming_request

## 3. Verification

- [x] 3.1 Run `uv run ruff check` and verify no errors
- [x] 3.2 Run `uv run ruff format` and verify formatting
- [x] 3.3 Run `uv run ty check` and verify no errors
- [x] 3.4 Run full test suite and verify all tests pass
