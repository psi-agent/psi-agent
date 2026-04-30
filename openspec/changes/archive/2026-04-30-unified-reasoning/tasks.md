## 1. Session Configuration

- [x] 1.1 Add `reasoning_effort` field to `SessionConfig` in `src/psi_agent/session/config.py` with default value "medium"
- [x] 1.2 Add `--reasoning-effort` CLI argument to session CLI in `src/psi_agent/session/cli.py`

## 2. Session Request Building

- [x] 2.1 Modify `_run_conversation` in `src/psi_agent/session/runner.py` to include `reasoning_effort` in request body
- [x] 2.2 Modify `_stream_conversation` in `src/psi_agent/session/runner.py` to include `reasoning_effort` in request body
- [x] 2.3 Modify `_complete_fn` in `src/psi_agent/session/runner.py` to include `reasoning_effort` in request body

## 3. OpenAI Completions Pass-through

- [x] 3.1 Verify `OpenAICompletionsClient.chat_completions` passes through `reasoning_effort` without modification
- [x] 3.2 Add test for `reasoning_effort` pass-through in `tests/ai/openai_completions/test_client.py`

## 4. Anthropic Messages Translation

- [x] 4.1 Add `REASONING_EFFORT_TO_BUDGET_TOKENS` mapping constant in `src/psi_agent/ai/anthropic_messages/translator.py`
- [x] 4.2 Modify `translate_openai_to_anthropic` to map `reasoning_effort` to `thinking.budget_tokens`
- [x] 4.3 Add tests for reasoning effort translation in `tests/ai/anthropic_messages/test_translator.py`

## 5. Integration Testing

- [x] 5.1 Add integration test verifying session includes `reasoning_effort` in AI requests
- [x] 5.2 Run full test suite to ensure no regressions
- [x] 5.3 Run `ruff check`, `ruff format`, and `ty check` to ensure code quality
