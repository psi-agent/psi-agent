## Why

psi-agent currently only supports OpenAI-compatible chat completion APIs through `psi-ai-openai-completions`. Anthropic's Claude API uses a different message format (Messages API) with distinct features like system prompts as a separate field, content blocks for multimodal input, and native tool use. Adding `psi-ai-anthropic-messages` enables native Anthropic API support, unlocking Claude-specific capabilities while maintaining the component architecture.

## What Changes

- Add new `psi-ai-anthropic-messages` component under `src/psi_agent/ai/anthropic_messages/`
- Implement HTTP server over Unix socket (same pattern as `psi-ai-openai-completions`)
- Implement Anthropic Messages API client with streaming support
- Add CLI entry point `psi-ai-anthropic-messages`
- Support Anthropic-specific features:
  - System prompt as separate parameter
  - Content blocks (text, image) for multimodal input
  - Native tool use with `tools` parameter
  - Streaming with `stream: true`

## Capabilities

### New Capabilities

- `anthropic-messages-server`: HTTP server for Anthropic Messages API over Unix socket, following the same architecture pattern as `psi-ai-openai-completions`
- `anthropic-messages-client`: Async client for Anthropic Messages API with streaming support, content blocks, and tool use

### Modified Capabilities

None. This is a new component with no changes to existing specs.

## Impact

- **New code**: `src/psi_agent/ai/anthropic_messages/` module with `__init__.py`, `config.py`, `client.py`, `server.py`, `cli.py`
- **Dependencies**: Add `anthropic` SDK to project dependencies
- **Entry points**: Add `psi-ai-anthropic-messages` CLI command to `pyproject.toml`
- **No breaking changes**: Existing components remain unchanged
