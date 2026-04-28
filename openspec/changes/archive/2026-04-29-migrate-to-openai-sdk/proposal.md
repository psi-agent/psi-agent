## Why

Currently, `psi-ai-anthropic-messages` uses the official `anthropic` SDK, while `psi-ai-openai-completions` uses a hand-rolled implementation with `aiohttp`. This inconsistency creates maintenance overhead and misses the benefits that the official OpenAI SDK provides: built-in error handling, retry logic, type safety, and streaming abstractions. The OpenAI SDK's async support (`AsyncOpenAI`) makes it a viable replacement that would simplify our codebase.

## What Changes

- Replace hand-rolled `aiohttp`-based HTTP client in `psi-ai-openai-completions` with the official `openai` SDK's `AsyncOpenAI` client
- Remove manual SSE parsing, error handling, and timeout management code
- Leverage SDK's built-in error types (`AuthenticationError`, `RateLimitError`, `APIConnectionError`, etc.)
- Maintain the same Unix socket server interface and OpenAI chat completions protocol

## Capabilities

### New Capabilities

None - this is an internal refactoring that improves implementation quality without changing external behavior.

### Modified Capabilities

None - the OpenAI completions component's requirements remain unchanged. It still:
- Accepts OpenAI chat completion format requests over Unix socket
- Supports both streaming and non-streaming responses
- Returns SSE-formatted streaming responses

## Impact

**Code Changes:**
- `src/psi_agent/ai/openai_completions/client.py` - Replace `aiohttp` with `AsyncOpenAI`
- `pyproject.toml` - Add `openai` dependency

**Code Reduction:**
- Estimated ~40% reduction in client.py lines (169 → ~100 lines)
- Remove manual SSE parsing logic
- Remove manual timeout configuration
- Simplify error handling with SDK exception types

**Dependencies:**
- Add: `openai` (official Python SDK with async support)
- Keep: `aiohttp` (still used by server.py for Unix socket HTTP server)

**No Breaking Changes:**
- External API remains identical (Unix socket + OpenAI chat completions protocol)
- Configuration interface unchanged
- CLI arguments unchanged
