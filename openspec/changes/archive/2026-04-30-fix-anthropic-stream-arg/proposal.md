## Why

The Anthropic Messages API client fails when making streaming requests because it incorrectly passes a `stream` parameter to `messages.stream()`. The Anthropic SDK's `.stream()` method doesn't accept a `stream` parameter—streaming is implied by using `.stream()` instead of `.create()`.

This causes a `TypeError: AsyncMessages.stream() got an unexpected keyword argument 'stream'` when attempting any streaming request through the Anthropic Messages adapter.

## What Changes

- Remove the `stream` key from the request body before passing it to `client.messages.stream()` in `AnthropicMessagesClient._stream_request()`

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

## Impact

- **Affected code**: `src/psi_agent/ai/anthropic_messages/client.py` — single line fix in `_stream_request()` method
- **API compatibility**: No API changes, purely internal fix
- **Dependencies**: No dependency changes
