## Why

Not all LLM models support `thinking` and `reasoning_effort` parameters. Adding these parameters at the session layer causes issues for models that don't recognize them. The reasoning parameters should be handled at the psi-ai-* layer where model-specific behavior can be properly configured.

## What Changes

- **BREAKING**: Remove `reasoning_effort` from SessionConfig and session CLI
- Remove `thinking` and `reasoning_effort` from session's AI request bodies
- Add `--thinking` and `--reasoning-effort` CLI arguments to psi-ai-* components
- psi-ai-* components inject reasoning parameters based on CLI configuration
- Default behavior: no reasoning parameters added (compatible with all models)

## Capabilities

### Modified Capabilities

- `unified-reasoning`: Move reasoning parameter handling from session to psi-ai-* layer
- `session-core`: Remove reasoning parameter injection from session
- `psi-ai-openai-completions`: Add CLI arguments for reasoning parameters, inject them when configured
- `anthropic-messages-client`: Add CLI arguments for reasoning parameters, inject them when configured

## Impact

- `src/psi_agent/session/config.py` - Remove `reasoning_effort` field
- `src/psi_agent/session/cli.py` - Remove `--reasoning-effort` argument
- `src/psi_agent/session/runner.py` - Remove `thinking` and `reasoning_effort` from request bodies
- `src/psi_agent/ai/openai_completions/config.py` - Add reasoning configuration fields
- `src/psi_agent/ai/openai_completions/cli.py` - Add reasoning CLI arguments
- `src/psi_agent/ai/openai_completions/server.py` - Inject reasoning parameters when configured
- `src/psi_agent/ai/anthropic_messages/config.py` - Add reasoning configuration fields
- `src/psi_agent/ai/anthropic_messages/cli.py` - Add reasoning CLI arguments
- `src/psi_agent/ai/anthropic_messages/server.py` - Inject reasoning parameters when configured