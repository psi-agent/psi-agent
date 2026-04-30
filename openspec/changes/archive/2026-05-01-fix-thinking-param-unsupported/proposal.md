## Why

The OpenAI completions AI component crashes when reasoning parameters (`thinking`, `reasoning_effort`) are configured, because these provider-specific parameters are passed directly to the official OpenAI SDK which doesn't recognize them. These parameters are extensions used by certain providers (like Anthropic via OpenRouter), but not part of the standard OpenAI API.

## What Changes

- Add parameter filtering in `OpenAICompletionsClient` to separate known OpenAI SDK parameters from extra parameters
- Pass extra parameters via the `extra_body` parameter supported by the OpenAI SDK
- This allows provider-specific extensions like `thinking` and `reasoning_effort` to work without crashing the SDK

## Capabilities

### New Capabilities

- `provider-specific-params`: Support for passing provider-specific parameters (like `thinking`, `reasoning_effort`) through the OpenAI SDK using `extra_body`

### Modified Capabilities

- `psi-ai-openai-completions`: Extend the AI component to properly handle non-standard API parameters without crashing

## Impact

- Affected files: `src/psi_agent/ai/openai_completions/client.py`
- No breaking changes - existing functionality remains intact
- Enables reasoning parameter support for compatible providers
