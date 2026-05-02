## Why

Codecov reports insufficient test coverage for the newly added code in PR #113 (ai-modules-review). The changes introduced new code paths that need test coverage:

1. **Session error handling**: New error chunk detection in `_parse_streaming_response` (lines 177-181) is not tested
2. **Translator tool_calls extraction**: New tool_use content block handling in `translate_anthropic_to_openai` needs coverage verification

## What Changes

- Add test for error chunk handling in session's `_parse_streaming_response`
- Verify coverage for new translator code (already has tests, may need edge cases)

## Capabilities

### New Capabilities

None - this is test coverage improvement for existing code.

### Modified Capabilities

None - no spec-level behavior changes.

## Impact

- `tests/session/test_runner.py` — Add test for streaming error chunk handling
- `tests/ai/anthropic_messages/test_translator.py` — Verify coverage for tool_use extraction (already added)