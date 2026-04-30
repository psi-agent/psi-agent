## Why

Codecov reports insufficient test coverage for the `_stream_request` method in `AnthropicMessagesClient`. The recent fix for the streaming parameter bug (PR #83) added code that is not covered by existing tests.

## What Changes

- Add tests for `_stream_request` method covering:
  - Successful streaming request with proper `stream` key removal
  - Streaming request error handling (authentication, rate limit, connection errors)
  - Model injection during streaming requests

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

## Impact

- **Affected code**: `tests/ai/anthropic_messages/test_client.py` — add new test cases
- **Coverage target**: Cover the `_stream_request` method and the `stream` key filtering logic
