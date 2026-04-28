## 1. Setup

- [x] 1.1 Create `src/psi_agent/channel/repl/` module directory
- [x] 1.2 Create `config.py` with `ReplConfig` dataclass

## 2. Client Implementation

- [x] 2.1 Create `client.py` with `ReplClient` class
- [x] 2.2 Implement async context manager for HTTP client
- [x] 2.3 Implement `send_message()` method for POST requests to session
- [x] 2.4 Add error handling for connection failures

## 3. REPL Loop Implementation

- [x] 3.1 Create `repl.py` with `Repl` class
- [x] 3.2 Implement async stdin reader
- [x] 3.3 Implement conversation history management
- [x] 3.4 Implement REPL loop with prompt, send, display
- [x] 3.5 Implement graceful exit (Ctrl+D and /quit)

## 4. CLI and Package

- [x] 4.1 Create `cli.py` with tyro CLI entry point
- [x] 4.2 Create `__init__.py` with public exports
- [x] 4.3 Add `psi-channel-repl` script entry to pyproject.toml

## 5. Testing

- [x] 5.1 Write unit tests for `ReplConfig`
- [x] 5.2 Write unit tests for `ReplClient` (mocked session)
- [x] 5.3 Write unit tests for `Repl` (mocked client and stdin)
- [x] 5.4 Run full test suite and verify all tests pass

## 6. Quality Checks

- [x] 6.1 Run `ruff check` and fix all lint errors
- [x] 6.2 Run `ruff format` and ensure code is formatted
- [x] 6.3 Run `ty check` and fix all type errors
