## Why

psi-session sends `"model": "session"` in the request body to psi-ai, but psi-ai-openai-completions forwards this directly to the upstream provider (OpenRouter), which rejects it as an invalid model ID. The actual model should be determined by psi-ai based on its configuration, not by the session.

## What Changes

- psi-ai-openai-completions will ignore the `model` field from incoming requests and use its configured model instead
- This allows session to use a placeholder model value without affecting the actual LLM provider

## Capabilities

### New Capabilities

<!-- No new capabilities -->

### Modified Capabilities

<!-- No spec-level requirement changes - this is a bug fix -->

## Impact

- `src/psi_agent/ai/openai_completions/server.py`: Override model field with configured model
