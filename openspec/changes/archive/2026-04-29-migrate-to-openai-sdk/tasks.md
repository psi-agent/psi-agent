## 1. Dependencies

- [x] 1.1 Add `openai` dependency to `pyproject.toml`
- [x] 1.2 Run `uv lock` to update lockfile

## 2. Client Implementation

- [x] 2.1 Replace `aiohttp.ClientSession` with `AsyncOpenAI` in `OpenAICompletionsClient.__init__`
- [x] 2.2 Update `__aenter__` to initialize `AsyncOpenAI` client
- [x] 2.3 Update `__aexit__` to close `AsyncOpenAI` client
- [x] 2.4 Refactor `_non_stream_request` to use SDK's `chat.completions.create()`
- [x] 2.5 Refactor `_stream_request` to use SDK's streaming API
- [x] 2.6 Update `_handle_error` to use SDK exception types

## 3. Testing

- [x] 3.1 Update existing unit tests for new client implementation
- [x] 3.2 Add tests for SDK error handling scenarios
- [x] 3.3 Run `ruff check` and `ruff format`
- [x] 3.4 Run `ty check` for type checking
- [x] 3.5 Run `pytest` to verify all tests pass

## 4. Verification

- [x] 4.1 Manual test with OpenAI API
- [x] 4.2 Manual test with OpenRouter API
- [x] 4.3 Verify streaming and non-streaming modes work correctly
