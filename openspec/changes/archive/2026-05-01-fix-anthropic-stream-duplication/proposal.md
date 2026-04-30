## Why

The Anthropic Messages AI component produces duplicated streaming content when using certain Anthropic-compatible providers (e.g., astron-code-latest). The SDK emits both `content_block_delta` events (incremental text) and `text` events (convenience events with snapshot), causing the same content to be streamed twice to the client.

## What Changes

- Filter out non-standard streaming events from Anthropic SDK before translation to OpenAI format
- Only process `content_block_delta` events for text content, ignore `text` convenience events

## Capabilities

### New Capabilities

- `anthropic-stream-filtering`: Filter Anthropic SDK streaming events to only process protocol-standard events

### Modified Capabilities

None - this is a bug fix, not a behavior change.

## Impact

- `src/psi_agent/ai/anthropic_messages/client.py` - filter events before yielding
- `src/psi_agent/ai/anthropic_messages/translator.py` - potentially add event type validation
