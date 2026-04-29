## Context

The `process_streaming_request` method returns `AsyncGenerator[str] | dict[str, Any]`. The caller in `server.py` uses `hasattr(stream_gen, "__aiter__")` to check if the result is an async generator, but ty cannot understand this control flow pattern.

## Goals / Non-Goals

**Goals:**
- Use `typing.cast` to explicitly narrow the type after runtime check
- Remove the `# ty: ignore` comment
- Maintain runtime behavior unchanged

**Non-Goals:**
- Change the return type signature of `process_streaming_request`
- Refactor the streaming logic

## Decisions

### Decision: Use `typing.cast` for type narrowing

**Rationale**: `typing.cast` tells the type checker "trust me, this value has this type at this point". Combined with the runtime `hasattr` check, this is type-safe and eliminates the need for ignore comments.

**Implementation**:
```python
from typing import cast
from collections.abc import AsyncGenerator

stream_gen = await self.runner.process_streaming_request(user_message)

if hasattr(stream_gen, "__aiter__"):
    async for chunk in cast(AsyncGenerator[str], stream_gen):
        await response.write(chunk.encode())
```

## Risks / Trade-offs

### Risk: cast bypasses type checking
**Mitigation**: The runtime check (`hasattr(stream_gen, "__aiter__")`) ensures the cast is valid
