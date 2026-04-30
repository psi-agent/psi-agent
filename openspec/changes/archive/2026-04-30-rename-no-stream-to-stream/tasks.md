## 1. CLI Parameter Rename

- [x] 1.1 Rename `no_stream` to `stream` in `src/psi_agent/channel/cli/cli.py`
- [x] 1.2 Rename `no_stream` to `stream` in `src/psi_agent/channel/repl/cli.py`
- [x] 1.3 Rename `no_stream` to `stream` in `src/psi_agent/channel/telegram/cli.py`

## 2. Internal Logic Update

- [x] 2.1 Update `not self.no_stream` to `self.stream` in channel CLI
- [x] 2.2 Update `not self.no_stream` to `self.stream` in REPL CLI
- [x] 2.3 Update `not self.no_stream` to `self.stream` in Telegram CLI

## 3. Docstring Update

- [x] 3.1 Update docstring for `stream` parameter in channel CLI
- [x] 3.2 Update docstring for `stream` parameter in REPL CLI
- [x] 3.3 Update docstring for `stream` parameter in Telegram CLI

## 4. Test Updates

- [x] 4.1 Update `tests/channel/cli/test_cli.py` to use `stream` parameter
- [x] 4.2 Update `tests/channel/repl/test_cli.py` to use `stream` parameter
- [x] 4.3 Update `tests/channel/telegram/test_cli.py` to use `stream` parameter

## 5. Quality Verification

- [x] 5.1 Run `ruff check` and `ruff format` to ensure code quality
- [x] 5.2 Run `ty check` to ensure type safety
- [x] 5.3 Run `pytest` to ensure all tests pass
