## Why

The `psi-ai-anthropic-messages` component is not functioning correctly as a protocol translator. It currently listens on `/v1/messages` (Anthropic format) but `psi-session` sends OpenAI chat completions format to `/v1/chat/completions`. The component should receive OpenAI format requests and translate them to Anthropic Messages format for upstream API calls.

## What Changes

- **BREAKING**: Change server endpoint from `/v1/messages` to `/v1/chat/completions`
- Add OpenAI-to-Anthropic request format translation in server
- Add Anthropic-to-OpenAI response format translation in client
- Update streaming SSE format from Anthropic events to OpenAI chunks
- Handle OpenAI-specific fields (e.g., `max_tokens` vs `max_completion_tokens`)

## Capabilities

### New Capabilities

- `openai-anthropic-translation`: Protocol translation between OpenAI chat completions and Anthropic messages formats

### Modified Capabilities

- `anthropic-messages-server`: Change endpoint from `/v1/messages` to `/v1/chat/completions`, add request translation
- `anthropic-messages-client`: Add response translation from Anthropic to OpenAI format

## Impact

- `src/psi_agent/ai/anthropic_messages/server.py` - Add `/v1/chat/completions` endpoint with request translation
- `src/psi_agent/ai/anthropic_messages/client.py` - Add response translation logic
- `openspec/specs/anthropic-messages-server/spec.md` - Update requirements for new endpoint
- `openspec/specs/anthropic-messages-client/spec.md` - Update requirements for response translation
- Tests will need updates for new format handling
