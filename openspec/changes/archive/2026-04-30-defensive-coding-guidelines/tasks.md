## 1. Guidelines Documentation

- [x] 1.1 Add defensive coding guidelines section (~20 lines) to CLAUDE.md

## 2. psi-session Component

- [x] 2.1 Fix null-safety in `session/runner.py` streaming delta content slicing (already done)
- [x] 2.2 Fix null-safety in `session/runner.py` `_reconstruct_tool_calls` (already done)
- [x] 2.3 Review and fix null-safety in `session/server.py` request handling
- [x] 2.4 Review and fix null-safety in `session/tool_executor.py` tool call processing

## 3. psi-ai Components

- [x] 3.1 Review and fix null-safety in `ai/openai_completions/client.py` streaming handling
- [x] 3.2 Review and fix null-safety in `ai/anthropic_messages/translator.py` response translation

## 4. psi-channel Components

- [x] 4.1 Review and fix null-safety in `channel/repl/client.py` streaming display
- [x] 4.2 Review and fix null-safety in `channel/telegram/client.py` streaming display
- [x] 4.3 Review and fix null-safety in `channel/cli/cli.py` streaming display

## 5. Testing and Quality

- [x] 5.1 Run existing test suite to verify no regressions
- [x] 5.2 Run `ruff check` to verify lint passes
- [x] 5.3 Run `ruff format` to verify formatting
- [x] 5.4 Run `ty check` to verify type checking passes
