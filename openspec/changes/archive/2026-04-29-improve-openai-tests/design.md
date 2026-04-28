## Context

The OpenAI completions client tests need to be refactored to match the testing pattern used in the Anthropic messages tests. Currently, the OpenAI tests construct real `httpx` objects to create exception instances, while the Anthropic tests use `unittest.mock.patch` to mock the entire SDK.

**Current OpenAI test pattern:**
```python
error = AuthenticationError(
    message="Invalid API key",
    response=_make_mock_response(401),
    body=None,
)
result = client._handle_error(error)
```

**Anthropic test pattern:**
```python
with patch("...AsyncAnthropic") as mock_anthropic:
    mock_instance = AsyncMock()
    mock_instance.messages.create = AsyncMock(side_effect=AuthenticationError(...))
    mock_anthropic.return_value = mock_instance

    async with client:
        result = await client.messages(...)
```

## Goals / Non-Goals

**Goals:**
- Refactor OpenAI tests to use `unittest.mock.patch` pattern
- Add tests for non-streaming requests, streaming requests, and model injection
- Ensure test coverage matches Anthropic tests
- Remove dependency on constructing real `httpx` objects

**Non-Goals:**
- Changing production code
- Adding new production features
- Modifying test configuration

## Decisions

### Decision 1: Use `unittest.mock.patch` for AsyncOpenAI

**Rationale:** Consistent with Anthropic tests, provides better isolation, and tests the full call chain.

**Pattern:**
```python
with patch("psi_agent.ai.openai_completions.client.AsyncOpenAI") as mock_openai:
    mock_instance = AsyncMock()
    mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_instance.close = AsyncMock()
    mock_openai.return_value = mock_instance
```

### Decision 2: Use class-based test organization

**Rationale:** Matches Anthropic test structure using `class TestOpenAICompletionsClient`.

## Risks / Trade-offs

**Risk: Mock path may be incorrect**
→ Mitigation: Verify the import path matches where `AsyncOpenAI` is used in client.py

**Trade-off: More verbose tests**
→ Acceptable: Better isolation and consistency with existing codebase
