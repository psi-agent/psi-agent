## Why

The psi-ai-* modules (openai_completions and anthropic_messages) have inconsistent logging patterns, a protocol translation bug, and error handling gaps that affect maintainability, correctness, and debugging.

### Issues Found

1. **Logging inconsistencies**: Streaming request handling lacks DEBUG logs for request bodies, streaming response completion logging is inconsistent with session module patterns, and there are redundant assertions in server startup code.

2. **Protocol translation bug**: `translate_anthropic_to_openai()` does not extract `tool_use` content blocks from Anthropic non-streaming responses. When the model makes a tool call, the response has `finish_reason: "tool_calls"` but no `message.tool_calls` field, breaking the OpenAI format contract.

3. **Error handling gap**: When AI modules yield an error chunk during streaming, the session module silently ignores it, leading to empty responses instead of error messages.

## What Changes

- Add DEBUG log for request body in `_stream_request` method of both client modules (parity with `_non_stream_request`)
- Add DEBUG log for streaming response completion in `_handle_streaming` method of both server modules (parity with session module)
- Remove redundant `assert self.client is not None` statements after assignment in both server modules
- Fix `translate_anthropic_to_openai()` to extract `tool_use` content blocks and populate `message.tool_calls`
- Handle error chunks in session's `_parse_streaming_response` instead of silently ignoring them

## Capabilities

### New Capabilities

None - this is a bug fix and code quality improvement.

### Modified Capabilities

**Fixed**: Non-streaming Anthropic responses now correctly include `tool_calls` in the message when the model makes tool calls. This ensures protocol parity with OpenAI responses.

## Impact

- `src/psi_agent/ai/openai_completions/client.py` — Add DEBUG log for streaming request body
- `src/psi_agent/ai/openai_completions/server.py` — Add DEBUG log for streaming completion, remove redundant assert
- `src/psi_agent/ai/anthropic_messages/client.py` — Add DEBUG log for streaming request body
- `src/psi_agent/ai/anthropic_messages/server.py` — Add DEBUG log for streaming completion, remove redundant assert
- `src/psi_agent/ai/anthropic_messages/translator.py` — Fix tool_use extraction in `translate_anthropic_to_openai`
- `src/psi_agent/session/runner.py` — Handle error chunks in streaming response parsing
- `tests/ai/anthropic_messages/test_translator.py` — Add tests for tool_calls translation
