## Context

PR #113 added new code paths that need test coverage:

1. **Session runner error handling** (`runner.py:177-181`): New code to detect and raise RuntimeError when streaming response contains an error chunk. This code path is not exercised by existing tests.

2. **Translator tool_use extraction** (`translator.py:210-223`): New code to extract tool_use content blocks and convert to tool_calls. Tests were added but we need to verify coverage.

## Goals / Non-Goals

**Goals:**
- Achieve 100% coverage for new code added in PR #113
- Specifically cover the error chunk handling in `_parse_streaming_response`

**Non-Goals:**
- Improving coverage for unrelated code
- Changing any production code

## Decisions

### Test error chunk handling

**Decision**: Add a test that mocks a streaming response containing an error chunk and verifies that RuntimeError is raised.

**Rationale**: The new error handling code raises RuntimeError when it detects `{"error": ...}` in a streaming chunk. We need to test this behavior.

**Implementation**: Use `aiohttp` mock response with error chunk data.

## Risks / Trade-offs

**Minimal risk**: Only adding tests, no production code changes.
