## Context

The streaming behavior changes introduced new code paths that lack sufficient test coverage. Additionally, manual review is needed to ensure CLAUDE.md compliance for patterns not caught by automated tools.

## Goals / Non-Goals

**Goals:**
- Achieve >90% patch coverage for modified files
- Ensure all code follows CLAUDE.md conventions
- Document any patterns that need manual enforcement

**Non-Goals:**
- Refactoring existing working code
- Adding new features
- Changing existing behavior

## Decisions

### Test Coverage Strategy

Focus on testing the uncovered code paths:
- `runner.py`: Streaming with tool calls, error handling, thinking block generation
- `client.py`: Streaming callback handling, error cases
- `repl.py`: Non-streaming mode, edge cases
- `cli.py`: Non-streaming mode paths

### CLAUDE.md Compliance Review

Review each modified file for:
1. Async interface compliance (all async functions, anyio for IO)
2. Type annotations (all functions must have them)
3. Docstring format (Google style)
4. Import order (stdlib, third-party, local)
5. Error handling (try-except with loguru)
6. Logging granularity (DEBUG for I/O, INFO for lifecycle)

## Risks / Trade-offs

- **Risk**: Tests may be brittle if they mock too much internal detail
  - **Mitigation**: Focus on behavior testing, not implementation details
