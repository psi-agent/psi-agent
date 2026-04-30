## 1. Session Layer Cleanup

- [x] 1.1 Remove `reasoning_effort` field from `SessionConfig` in `src/psi_agent/session/config.py`
- [x] 1.2 Remove `--reasoning-effort` CLI argument from `src/psi_agent/session/cli.py`
- [x] 1.3 Remove `thinking` and `reasoning_effort` from `_run_conversation` request body in `src/psi_agent/session/runner.py`
- [x] 1.4 Remove `thinking` and `reasoning_effort` from `_stream_conversation` request body in `src/psi_agent/session/runner.py`
- [x] 1.5 Remove `thinking` and `reasoning_effort` from `_complete_fn` request body in `src/psi_agent/session/runner.py`

## 2. OpenAI Completions AI Layer

- [x] 2.1 Add `thinking` and `reasoning_effort` fields to `OpenAICompletionsConfig` in `src/psi_agent/ai/openai_completions/config.py`
- [x] 2.2 Add `--thinking` and `--reasoning-effort` CLI arguments in `src/psi_agent/ai/openai_completions/cli.py`
- [x] 2.3 Modify server to inject reasoning parameters when configured in `src/psi_agent/ai/openai_completions/server.py`

## 3. Anthropic Messages AI Layer

- [x] 3.1 Add `thinking` and `reasoning_effort` fields to `AnthropicMessagesConfig` in `src/psi_agent/ai/anthropic_messages/config.py`
- [x] 3.2 Add `--thinking` and `--reasoning-effort` CLI arguments in `src/psi_agent/ai/anthropic_messages/cli.py`
- [x] 3.3 Modify server to inject reasoning parameters when configured in `src/psi_agent/ai/anthropic_messages/server.py`

## 4. Testing

- [x] 4.1 Update session tests to remove reasoning parameter assertions
- [x] 4.2 Add tests for OpenAI completions reasoning parameter injection
- [x] 4.3 Add tests for Anthropic messages reasoning parameter injection
- [x] 4.4 Run full test suite to ensure no regressions
- [x] 4.5 Run `ruff check`, `ruff format`, and `ty check` to ensure code quality
