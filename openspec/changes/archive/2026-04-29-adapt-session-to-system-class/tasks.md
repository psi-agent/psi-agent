## 1. System Instance Management

- [x] 1.1 Add `_system` attribute to `SessionRunner` class
- [x] 1.2 Create `_load_system()` function to instantiate `System` class
- [x] 1.3 Call `_load_system()` in `SessionRunner.__aenter__()`
- [x] 1.4 Update `_handle_workspace_changes()` to re-instantiate `System` on system.py changes

## 2. System Prompt Integration

- [x] 2.1 Replace `load_system_prompt()` with `system.build_system_prompt()` call
- [x] 2.2 Update `_system_prompt_cache` assignment to use instance method

## 3. History Compaction Integration

- [x] 3.1 Add `_complete_fn()` method for LLM-based summarization
- [x] 3.2 Call `system.compact_history()` in `_build_messages()`
- [x] 3.3 Pass `complete_fn` to `compact_history()`

## 4. Validation

- [x] 4.1 Run `ruff check` to verify code style
- [x] 4.2 Run `ruff format` to format code
- [x] 4.3 Run `ty check` to verify types
