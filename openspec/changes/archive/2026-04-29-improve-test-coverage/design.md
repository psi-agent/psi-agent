## Context

Current test coverage is 59% overall, with significant gaps in critical modules:

| Module | Coverage | Key Missing Areas |
|--------|----------|-------------------|
| session/runner.py | 27% | Core agent loop, message handling, tool calling |
| session/server.py | 30% | HTTP server, request handling |
| workspace/snapshot/api.py | 28% | Snapshot creation, layer management |
| workspace/umount/api.py | 31% | Unmount operations, cleanup |
| session/tool_executor.py | 41% | Tool execution, error handling |
| channel/cli/cli.py | 39% | CLI subcommands |

The codebase uses pytest with pytest-asyncio for async tests. Existing tests provide good patterns to follow.

## Goals / Non-Goals

**Goals:**
- Increase overall coverage to 80%+
- Focus on core business logic (session runner, tool execution, workspace operations)
- Add tests for error paths and edge cases
- Ensure all async operations are properly tested

**Non-Goals:**
- 100% coverage (not practical for CLI entry points and some error paths)
- Changing production code behavior
- Adding integration tests that require external services

## Decisions

### 1. Test Organization
Follow existing pattern: `tests/<module>/test_<file>.py` mirrors `src/psi_agent/<module>/<file>.py`.

### 2. Mocking Strategy
- Use `unittest.mock.AsyncMock` for async functions
- Use `aiohttp.test_utils.AioHTTPTestCase` or `pytest-aiohttp` for HTTP servers
- Mock external dependencies (filesystem, subprocess) rather than using real resources

### 3. Priority Order
Focus on modules by impact:
1. **session/runner.py** - Core agent loop, highest impact
2. **session/server.py** - HTTP interface
3. **workspace/snapshot/api.py** - Critical workspace operation
4. **workspace/umount/api.py** - Cleanup operations
5. **session/tool_executor.py** - Tool execution
6. **channel/telegram/bot.py** - Telegram integration

### 4. Coverage Targets Per Module
- Core logic (runner, executor): 80%+
- Server/handlers: 70%+
- CLI entry points: 50%+ (mainly smoke tests)

## Risks / Trade-offs

- **Risk**: Tests may become brittle if they mock too much → Mitigation: Focus on behavior, not implementation details
- **Risk**: Async test complexity → Mitigation: Use pytest-asyncio fixtures consistently
- **Risk**: Coverage doesn't guarantee correctness → Mitigation: Write meaningful assertions, test edge cases
