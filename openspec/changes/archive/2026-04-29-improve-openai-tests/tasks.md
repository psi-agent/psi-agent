## 1. Refactor Test Structure

- [x] 1.1 Convert test file to class-based structure (`TestOpenAICompletionsClient`)
- [x] 1.2 Add `pytest.fixture` for config and client

## 2. Add Mock-Based Tests

- [x] 2.1 Add test for async context manager with mocked `AsyncOpenAI`
- [x] 2.2 Add test for non-streaming request with mocked response
- [x] 2.3 Add test for streaming request with mocked stream
- [x] 2.4 Add test for model injection

## 3. Add Error Handling Tests

- [x] 3.1 Add test for authentication error with mocked SDK
- [x] 3.2 Add test for rate limit error with mocked SDK
- [x] 3.3 Add test for connection error with mocked SDK
- [x] 3.4 Add test for timeout error with mocked SDK

## 4. Verification

- [x] 4.1 Run `ruff check` and `ruff format`
- [x] 4.2 Run `pytest` to verify all tests pass
