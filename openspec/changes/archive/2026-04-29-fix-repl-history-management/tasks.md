## 1. Update REPL Client API

- [x] 1.1 Change `send_message` signature to accept single message string instead of message list
- [x] 1.2 Update request body to contain messages array with single user message
- [x] 1.3 Update log message to reflect single message being sent

## 2. Update REPL Class

- [x] 2.1 Remove `self.history` attribute from `Repl` class
- [x] 2.2 Remove history append logic in `run()` method
- [x] 2.3 Update `send_message` call to pass single user input string

## 3. Update Tests

- [x] 3.1 Update `tests/channel/repl/test_client.py` to test new single-message API
- [x] 3.2 Update `tests/channel/repl/test_repl.py` to remove history-related tests
- [x] 3.3 Run all tests to verify changes

## 4. Update Spec

- [x] 4.1 Update `openspec/specs/repl-channel/spec.md` to reflect new behavior (remove history management requirement)
