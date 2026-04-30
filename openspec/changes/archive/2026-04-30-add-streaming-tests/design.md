## Context

The `_stream_request` method in `AnthropicMessagesClient` was recently modified to filter out the `stream` key before calling `messages.stream()`. This code path has no test coverage, causing codecov to report insufficient patch coverage.

## Goals / Non-Goals

**Goals:**
- Add tests for `_stream_request` method
- Cover the `stream` key filtering logic
- Cover error handling in streaming requests

**Non-Goals:**
- No changes to production code
- No changes to other test files

## Decisions

**Use mock for Anthropic SDK streaming API**

The tests will mock `AsyncAnthropic` and its `messages.stream()` method to avoid making real API calls. This follows the existing pattern in `test_client.py`.

## Risks / Trade-offs

No risks. This is purely adding test coverage.
