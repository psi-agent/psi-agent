## 1. Configuration

- [x] 1.1 Add `history_file` optional field to `ReplConfig` dataclass
- [x] 1.2 Add `get_history_path()` method to return default or configured path

## 2. History Management

- [x] 2.1 Create helper function to ensure history directory exists
- [x] 2.2 Replace `InMemoryHistory` with `FileHistory` in `Repl.__init__`
- [x] 2.3 Pass history file path to `PromptSession` constructor

## 3. Testing

- [x] 3.1 Add unit tests for `ReplConfig.get_history_path()`
- [x] 3.2 Add unit tests for history directory creation
- [x] 3.3 Add integration tests for persistent history across sessions
- [x] 3.4 Run full test suite to verify no regressions

## 4. Quality Assurance

- [x] 4.1 Run `ruff check` to verify lint compliance
- [x] 4.2 Run `ruff format` to verify formatting
- [x] 4.3 Run `ty check` to verify type checking
