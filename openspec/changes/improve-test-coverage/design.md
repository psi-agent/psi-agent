## Context

Current test coverage is 85% with 511 tests passing. The coverage report shows:
- CLI modules have the lowest coverage (39-69%)
- Server/client implementations have moderate coverage (63-79%)
- Core business logic has good coverage (85%+)

The main challenge is testing CLI entry points which require mocking the actual execution flow.

## Goals / Non-Goals

**Goals:**
- Increase overall coverage from 85% to 90%+
- Add tests for CLI modules with coverage below 70%
- Add tests for API modules with coverage below 80%
- Focus on practical test cases that catch real bugs

**Non-Goals:**
- 100% coverage (not practical or valuable)
- Changing production code
- Adding integration tests that require external services

## Decisions

### Decision 1: Use mocking for CLI tests

**Rationale:** CLI entry points call `asyncio.run()` and other side effects. Mocking allows testing the configuration flow without actual execution.

**Implementation:**
- Mock `asyncio.run()` to prevent actual async execution
- Mock the main component classes (e.g., `TelegramBot`, `SessionRunner`)
- Test that correct configuration is passed to components

### Decision 2: Focus on error handling paths

**Rationale:** Many uncovered lines are error handling and edge cases. These are important for robustness.

**Implementation:**
- Add tests for error conditions (missing arguments, invalid config)
- Add tests for exception handling in server/client code
- Use `pytest.raises()` for expected exceptions

### Decision 3: Prioritize by coverage impact

**Rationale:** Focus on modules with lowest coverage first for maximum impact.

**Priority order:**
1. `channel/cli/cli.py` (39%) - highest impact
2. `ai/*/cli.py` (52-53%)
3. `session/cli.py` (52%)
4. `workspace/*/api.py` (63-78%)
5. `ai/*/server.py` and `ai/*/client.py` (65-79%)

## Risks / Trade-offs

- **Risk:** Tests may be brittle if they over-mock internal implementation details
  - Mitigation: Focus on testing behavior, not implementation

- **Risk:** Adding tests increases maintenance burden
  - Mitigation: Keep tests simple and focused on critical paths
