## Why

Different LLM models have inconsistent default reasoning behavior - some enable extended thinking by default while others don't. This creates unpredictable agent behavior when switching models. We need session to uniformly enable reasoning for all requests, and AI components to pass through the reasoning parameter without modification.

## What Changes

- Session will add `reasoning_effort` parameter to all AI requests by default
- AI components (openai-completions, anthropic-messages) will pass through `reasoning_effort` parameter to upstream APIs without modification
- No model-specific logic in AI components - they act as transparent proxies for this parameter

## Capabilities

### New Capabilities

- `unified-reasoning`: Session uniformly enables reasoning for all AI requests, ensuring consistent extended thinking behavior across different LLM providers

### Modified Capabilities

- `session-core`: Session now adds `reasoning_effort` parameter to AI requests
- `psi-ai-openai-completions`: Pass through `reasoning_effort` parameter to upstream API
- `anthropic-messages-client`: Pass through `reasoning_effort` parameter to Anthropic API (mapped to appropriate Anthropic parameter if needed)

## Impact

- `src/psi_agent/session/runner.py` - Add `reasoning_effort` to request body
- `src/psi_agent/session/config.py` - Add reasoning configuration option
- `src/psi_agent/ai/openai_completions/client.py` - Pass through reasoning parameter
- `src/psi_agent/ai/anthropic_messages/client.py` - Pass through reasoning parameter
- `src/psi_agent/ai/anthropic_messages/translator.py` - Handle reasoning parameter translation
