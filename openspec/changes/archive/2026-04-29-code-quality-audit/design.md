## Context

The codebase consists of 57 Python files across 5 main components (ai, channel, session, utils, workspace). CLAUDE.md defines comprehensive coding standards including:

1. **Type annotations**: All files must start with `from __future__ import annotations` and use modern union syntax (`X | Y`)
2. **Import ordering**: stdlib → third-party → local, alphabetically sorted within each group
3. **Async patterns**: All IO must use async methods (anyio, aiohttp, asyncio.subprocess)
4. **Docstrings**: Google style format
5. **Logging**: loguru with specific granularity standards
6. **CLI**: tyro with sensitive argument masking

The audit identified violations across multiple categories.

## Goals / Non-Goals

**Goals:**
- Document all code quality violations found during the audit
- Provide a clear task list for fixing each category of violations
- Establish patterns for future code to follow

**Non-Goals:**
- Refactoring or architectural changes
- Adding new features or capabilities
- Changing existing behavior

## Decisions

### D1: Fix violations incrementally by category

**Rationale**: Fixing by category (imports, then annotations, then docstrings) ensures consistent progress and makes review easier. Each PR can focus on one type of fix.

**Alternatives considered**:
- Fix by file: Harder to review, mixes different types of changes
- Fix all at once: Too large for effective review

### D2: Use ruff for automated formatting

**Rationale**: ruff already configured in project. It handles import sorting (isort) and formatting automatically.

### D3: Manual review for complex cases

**Rationale**: Some violations (like missing type annotations on complex functions) require human judgment. Automated tools can't infer all types correctly.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Type annotation changes may break ty check | Run ty check after each batch of fixes |
| Import reordering may cause circular imports | Test imports after reordering |
| Docstring changes may affect generated docs | Verify doc generation still works |

## Audit Findings Summary

### Category 1: Missing `from __future__ import annotations`

All 57 files correctly include this import at the top of the file. **No violations found.**

### Category 2: Import Ordering

Files with import ordering issues:
- `ai/__init__.py`: Local imports before third-party (tyro.conf imported after psi_agent.*)
- `channel/__init__.py`: Same issue
- `session/__init__.py`: Same issue
- `workspace/__init__.py`: Same issue
- `__main__.py`: tyro.conf imported after local imports

### Category 3: Type Annotations

Files with type annotation issues:
- `ai/openai_completions/server.py:156`: Uses `Path()` instead of `anyio.Path()` for sync operation
- `channel/cli/cli.py:88`: Duplicate import of `json` inside function
- `channel/cli/cli.py:90`: Duplicate import of `logger` inside function
- `session/runner.py:426`: Return type `Any` instead of specific type for streaming
- `session/schedule.py`: Uses `datetime.now()` which is sync (should use async alternative)

### Category 4: Docstring Formatting

Files with docstring issues:
- `workspace/manifest.py`: `ManifestParseError` class has docstring on `pass` statement (line 15)
- `workspace/pack/api.py`: `PackError` class has docstring on `pass` statement (line 19)
- `workspace/mount/api.py`: `MountError` class has docstring on `pass` statement (line 19)
- `workspace/snapshot/api.py`: `SnapshotError` class has docstring on `pass` statement (line 19)
- `workspace/umount/api.py`: `UmountError` class has docstring on `pass` statement (line 19)
- `workspace/unpack/api.py`: `UnpackError` class has docstring on `pass` statement (line 19)

### Category 5: Async Context Manager Patterns

All async context managers correctly:
- Initialize resource in `__aenter__`
- Close and set to `None` in `__aexit__`
- Log debug messages

**No violations found.**

### Category 6: CLI Sensitive Argument Masking

Files missing sensitive argument masking:
- `channel/cli/cli.py`: No sensitive args to mask (OK)
- `channel/repl/cli.py`: No sensitive args to mask (OK)
- `session/cli.py`: No sensitive args to mask (OK)
- `workspace/*/cli.py`: No sensitive args to mask (OK)

Files with correct masking:
- `ai/anthropic_messages/cli.py`: Correctly masks `api_key`
- `ai/openai_completions/cli.py`: Correctly masks `api_key`
- `channel/telegram/cli.py`: Correctly masks `token`

**No violations found.**

### Category 7: Logging Granularity

Files with potential logging issues:
- Most files follow the granularity standards correctly
- `session/runner.py`: Uses `logger.exception()` appropriately in error handlers
- All components log request/response bodies at DEBUG level with sensitive data masked

**No significant violations found.**
