## 1. Dependencies

- [x] 1.1 Add `prompt-toolkit` dependency to pyproject.toml
- [x] 1.2 Run `uv lock` to update lock file

## 2. Core Implementation

- [x] 2.1 Update `Repl` class to use `PromptSession` from prompt-toolkit
- [x] 2.2 Replace `_read_input()` method with `prompt_async()` call
- [x] 2.3 Configure `InMemoryHistory` for session history
- [x] 2.4 Set up prompt with `"> "` prompt string

## 3. Multi-line Support

- [x] 3.1 Enable multi-line input with Meta+Enter binding
- [x] 3.2 Ensure line breaks are preserved in submitted messages

## 4. Testing

- [x] 4.1 Update existing tests to work with new async input method
- [x] 4.2 Add tests for history navigation behavior
- [x] 4.3 Add tests for line editing behavior
- [x] 4.4 Run full test suite to verify no regressions

## 5. Quality Checks

- [x] 5.1 Run `ruff check` to verify lint compliance
- [x] 5.2 Run `ruff format` to verify formatting
- [x] 5.3 Run `ty check` to verify type checking
