## Why

The OpenAI completions client tests use a different style than the Anthropic messages tests. The Anthropic tests use `unittest.mock.patch` to mock the entire SDK, providing comprehensive test coverage without needing real API calls. The OpenAI tests currently construct real exception objects with `httpx` dependencies, which is inconsistent and less thorough. This change aligns the OpenAI tests with the Anthropic test patterns for consistency and better coverage.

## What Changes

- Refactor `tests/ai/openai_completions/test_client.py` to use `unittest.mock.patch` pattern
- Mock `AsyncOpenAI` client instead of constructing real exception objects
- Add tests for non-streaming requests, streaming requests, and model injection
- Ensure test coverage matches or exceeds the Anthropic tests

## Capabilities

### New Capabilities

None - this is a test improvement with no new production capabilities.

### Modified Capabilities

None - test behavior changes don't affect spec-level requirements.

## Impact

**Code Changes:**
- `tests/ai/openai_completions/test_client.py` - Refactor to use mock pattern

**No Breaking Changes:**
- Production code unchanged
- Test file only
