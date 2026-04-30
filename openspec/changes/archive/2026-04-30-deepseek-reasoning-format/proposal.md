## Why

DeepSeek uses a specific reasoning API format that differs from what we currently support. The current implementation only adds `reasoning_effort` but misses the `thinking` toggle and uses incorrect parameter mapping for Anthropic format. We need to align with DeepSeek's actual API format to ensure proper reasoning behavior across all providers.

## What Changes

- Session will add both `thinking: {"type": "enabled"}` (reasoning toggle) and `reasoning_effort` to all AI requests
- OpenAI completions will pass through both parameters unchanged (DeepSeek accepts this format)
- Anthropic translator will map `reasoning_effort` to `output_config.effort` instead of `thinking.budget_tokens`
- **BREAKING**: Remove `REASONING_EFFORT_TO_BUDGET_TOKENS` mapping (no longer used)

## Capabilities

### Modified Capabilities

- `unified-reasoning`: Update to support DeepSeek's reasoning format with both toggle and effort parameters
- `psi-ai-openai-completions`: Pass through `thinking` toggle parameter
- `anthropic-messages-client`: Map `reasoning_effort` to `output_config.effort`

## Impact

- `src/psi_agent/session/runner.py` - Add `thinking: {"type": "enabled"}` to request body
- `src/psi_agent/ai/anthropic_messages/translator.py` - Change mapping from `thinking.budget_tokens` to `output_config.effort`
- Tests need to be updated to reflect new parameter structure