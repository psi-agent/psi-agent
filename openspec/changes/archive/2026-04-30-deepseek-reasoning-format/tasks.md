## 1. Session Request Building

- [x] 1.1 Modify `_run_conversation` in `src/psi_agent/session/runner.py` to add `thinking: {"type": "enabled"}` to request body
- [x] 1.2 Modify `_stream_conversation` in `src/psi_agent/session/runner.py` to add `thinking: {"type": "enabled"}` to request body
- [x] 1.3 Modify `_complete_fn` in `src/psi_agent/session/runner.py` to add `thinking: {"type": "enabled"}` to request body

## 2. Anthropic Messages Translation

- [x] 2.1 Remove `REASONING_EFFORT_TO_BUDGET_TOKENS` constant from `src/psi_agent/ai/anthropic_messages/translator.py`
- [x] 2.2 Modify `translate_openai_to_anthropic` to map `reasoning_effort` to `output_config.effort`
- [x] 2.3 Modify `translate_openai_to_anthropic` to pass through `thinking` parameter

## 3. Testing

- [x] 3.1 Update tests in `tests/session/test_runner.py` to verify `thinking` toggle is included
- [x] 3.2 Update tests in `tests/ai/anthropic_messages/test_translator.py` to verify new mapping
- [x] 3.3 Run full test suite to ensure no regressions
- [x] 3.4 Run `ruff check`, `ruff format`, and `ty check` to ensure code quality
