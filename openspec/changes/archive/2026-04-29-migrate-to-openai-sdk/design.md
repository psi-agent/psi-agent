## Context

The `psi-ai-openai-completions` component currently implements HTTP communication with OpenAI-compatible APIs using raw `aiohttp`. This requires manual handling of:

- Request/response serialization
- SSE (Server-Sent Events) parsing for streaming
- Error type detection and mapping
- Timeout configuration
- Connection management

In contrast, `psi-ai-anthropic-messages` uses the official `anthropic` SDK which provides these features out-of-the-box. The OpenAI Python SDK (`openai>=1.0.0`) now has mature async support via `AsyncOpenAI` client, making it suitable for our async-first architecture.

**Current Implementation Analysis:**

| Aspect | Hand-rolled (aiohttp) | SDK (AsyncOpenAI) |
|--------|----------------------|-------------------|
| Lines of code | ~169 | ~100 (estimated) |
| Error types | Manual mapping | Built-in hierarchy |
| SSE parsing | Manual line parsing | SDK handles |
| Retry logic | None | Built-in with backoff |
| Type safety | Dict[str, Any] | Typed responses |
| Streaming | Manual chunk handling | Async generators |

## Goals / Non-Goals

**Goals:**
- Replace `aiohttp` with `AsyncOpenAI` in `OpenAICompletionsClient`
- Reduce code complexity and maintenance burden
- Gain built-in retry logic and error handling
- Maintain identical external behavior (Unix socket server, OpenAI protocol)

**Non-Goals:**
- Changing the server implementation (still uses aiohttp for Unix socket)
- Modifying the configuration interface
- Adding new features beyond what SDK provides
- Changing the anthropic implementation

## Decisions

### Decision 1: Use `AsyncOpenAI` client

**Rationale:** The official SDK provides:
- Type-safe request/response handling
- Built-in streaming with async generators
- Comprehensive error type hierarchy
- Automatic retry with exponential backoff
- Connection pooling

**Alternatives considered:**
- Keep `aiohttp`: More control but more maintenance, no retry logic
- Use `httpx`: Still requires manual SSE parsing, no OpenAI-specific features

### Decision 2: Keep `aiohttp` for server component

**Rationale:** The server component (`OpenAICompletionsServer`) uses aiohttp's `web.Application` for Unix socket HTTP serving. The OpenAI SDK doesn't provide server functionality - it's purely a client library.

### Decision 3: Use SDK's streaming API with `stream=True`

**Rationale:** The SDK's `stream=True` parameter returns an async iterator that handles SSE parsing automatically. We convert SDK stream events to our SSE format for compatibility with the session component.

**Code pattern:**
```python
async with client.chat.completions.create(..., stream=True) as stream:
    async for chunk in stream:
        # Convert to SSE format
        yield f"data: {chunk.model_dump_json()}\n\n"
```

## Risks / Trade-offs

**Risk: SDK breaking changes**
→ Mitigation: Pin SDK version in `pyproject.toml`, test before upgrading

**Risk: Different error response format**
→ Mitigation: SDK exceptions have consistent structure; map to our error dict format

**Risk: Streaming format differences**
→ Mitigation: Test with multiple providers (OpenAI, OpenRouter, local models)

**Trade-off: Additional dependency**
→ Acceptable: The SDK is well-maintained and widely used; reduces our maintenance burden
