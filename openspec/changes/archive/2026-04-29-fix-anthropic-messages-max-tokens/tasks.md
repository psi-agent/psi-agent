## 1. Implementation

- [x] 1.1 Add `max_tokens` field to `AnthropicMessagesConfig` with default value 4096
- [x] 1.2 Add `max_tokens` parameter to CLI dataclass with default value 4096
- [x] 1.3 Pass `max_tokens` from config to translator and use as default when not provided in request
- [x] 1.4 Fix model replacement logic in client to replace `"session"` placeholder
- [x] 1.5 Add unit tests for translator with and without `max_tokens`
- [x] 1.6 Add unit tests for model placeholder replacement

## 2. Verification

- [x] 2.1 Run `ruff check` and `ruff format` to ensure code quality
- [x] 2.2 Run `ty check` for type checking
- [x] 2.3 Run `pytest` to verify all tests pass
- [x] 2.4 Manually test the fix with the provided commands
