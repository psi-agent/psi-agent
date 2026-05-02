## 1. CLI Module Refactoring

- [x] 1.1 Create `src/psi_agent/channel/cli/config.py` with `CliConfig` dataclass
- [x] 1.2 Create `src/psi_agent/channel/cli/client.py` with `CliClient` class
- [x] 1.3 Refactor `src/psi_agent/channel/cli/cli.py` to use `CliConfig` and `CliClient`
- [x] 1.4 Create `src/psi_agent/channel/cli/__init__.py` with module exports

## 2. Logging Consistency

- [x] 2.1 Add INFO level startup log to cli.py (`logger.info("Starting psi-channel-cli")`)
- [x] 2.2 Add connector close logging to `ReplClient.__aexit__`
- [x] 2.3 Add connector close logging to `TelegramClient.__aexit__`
- [x] 2.4 Add connector close logging to new `CliClient.__aexit__`

## 3. Request Body Consistency

- [x] 3.1 Add `"model": "session"` field to `ReplClient.send_message()` request body
- [x] 3.2 Add `"model": "session"` field to `ReplClient.send_message_stream()` request body
- [x] 3.3 Ensure `CliClient` includes `"model": "session"` in request body

## 4. Error Response Format Consistency

- [x] 4.1 Update `cli.py` error messages to use consistent format
- [x] 4.2 Verify `ReplClient` error messages use consistent format
- [x] 4.3 Verify `TelegramClient` error messages use consistent format

## 5. Streaming Content Handling Consistency

- [x] 5.1 Update `cli.py` streaming handler to use `if content is not None` check before append
- [x] 5.2 Update `ReplClient` streaming handler to use `if content is not None` check before append
- [x] 5.3 Update `TelegramClient` streaming handler to use `if content is not None` check before append

## 6. Module Exports

- [x] 6.1 Update `src/psi_agent/channel/telegram/__init__.py` to export `Telegram`, `TelegramConfig`, `TelegramClient`
- [x] 6.2 Verify `src/psi_agent/channel/repl/__init__.py` exports are correct
- [x] 6.3 Verify new `src/psi_agent/channel/cli/__init__.py` exports are correct

## 7. Testing

- [x] 7.1 Run `ruff check` to verify no lint errors
- [x] 7.2 Run `ruff format` to verify formatting
- [x] 7.3 Run `ty check` to verify type checking
- [x] 7.4 Run `pytest` to verify all tests pass
- [ ] 7.5 Test CLI channel manually with session (requires running session)
- [ ] 7.6 Test REPL channel manually with session (requires running session)
- [ ] 7.7 Test Telegram channel manually with session (requires running session)