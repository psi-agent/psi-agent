## 1. Fix Import Placement

- [x] 1.1 Fix `tests/ai/anthropic_messages/test_translator.py` - move StreamingTranslator import to header
- [x] 1.2 Fix `tests/session/test_history.py` - move patch import to header
- [x] 1.3 Fix `tests/session/test_runner.py` - move ChangeSummary, MagicMock imports to header
- [x] 1.4 Fix `tests/session/test_server.py` - move SessionRunner, web imports to header

## 2. Verification

- [x] 2.1 Run `uv run ruff check` and verify no errors
- [x] 2.2 Run `uv run ty check` and verify no errors
- [x] 2.3 Run tests and verify all pass
