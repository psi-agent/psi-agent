## Context

The Anthropic Python SDK's streaming API emits multiple event types for text content:
1. `content_block_delta` - Standard protocol events containing incremental text deltas
2. `text` - Convenience events with `snapshot` field showing accumulated text

When using certain Anthropic-compatible providers (like astron-code-latest), both event types are emitted for the same content. Our current implementation in `client.py` yields all events from the SDK, and the translator only processes `content_block_delta`, but the `text` events still appear in logs and may cause confusion.

The root cause: the `anthropic_event_stream()` generator in `client.py` yields ALL events from the SDK without filtering.

## Goals / Non-Goals

**Goals:**
- Filter out non-standard events (`text`, `snapshot`) before yielding to translator
- Only yield protocol-standard events that the translator expects

**Non-Goals:**
- Changing the translator logic (it already correctly ignores unknown events)
- Modifying any other AI provider implementations

## Decisions

**Decision 1: Filter events in client.py before yielding**

Rationale: The translator's job is to convert Anthropic events to OpenAI format. It shouldn't need to know about SDK-specific convenience events. Filtering at the source (client) keeps the translator focused on protocol translation.

Alternative considered: Filter in translator - rejected because it mixes protocol concerns with SDK-specific quirks.

**Decision 2: Maintain a whitelist of known event types**

Known standard events from Anthropic Messages API:
- `message_start`
- `content_block_start`
- `content_block_delta`
- `content_block_stop`
- `message_delta`
- `message_stop`
- `ping` (keep-alive)

Events to filter out:
- `text` (SDK convenience event)
- Any other unknown events

## Risks / Trade-offs

- **Risk**: Future SDK versions may introduce new standard events
  - Mitigation: Log filtered events at DEBUG level for visibility; update whitelist when new events are documented
