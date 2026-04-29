## Context

The psi-agent codebase follows a comprehensive set of coding standards documented in CLAUDE.md. These standards cover Python version requirements, code style, async patterns, import ordering, type annotations, docstrings, error handling, logging, CLI design, and testing. A full audit of all 56 Python source files and 42 test files was conducted to assess compliance.

The audit revealed that the codebase generally follows the standards well, with a few specific areas needing attention. This design document outlines the approach for addressing identified issues.

## Goals / Non-Goals

**Goals:**
- Document all code standards violations found during the audit
- Establish a remediation plan with clear priorities
- Identify patterns that could benefit from automated enforcement
- Provide recommendations for maintaining standards compliance

**Non-Goals:**
- Automatically fix all violations (manual review needed for some)
- Add new coding standards not already in CLAUDE.md
- Modify existing functionality or behavior

## Decisions

### 1. Import Order Remediation

**Decision**: Fix import order violations using ruff's isort (I rule) automatically.

**Rationale**: Ruff already handles import sorting. The violations found are cases where the code was written before strict enforcement or where ruff was not run.

**Files Affected**:
- `session/runner.py` - imports `importlib.util`, `sys` after third-party
- `session/schedule.py` - imports `asyncio`, `re`, `dataclass`, `datetime`, `pathlib` mixed with third-party
- `workspace/mount/api.py` - imports `asyncio`, `tempfile`, `pathlib`, `uuid` after third-party
- `workspace/snapshot/api.py` - imports `asyncio`, `shutil`, `tempfile`, `pathlib`, `uuid` after third-party
- `workspace/umount/api.py` - imports `asyncio`, `pathlib` after third-party

### 2. Async Context Manager Pattern Fix

**Decision**: Update `__aexit__` methods to set resource references to `None` after cleanup.

**Rationale**: The CLAUDE.md specifies this pattern for proper resource cleanup and debugging. Two client files are missing this for `_connector`.

**Files Affected**:
- `channel/repl/client.py:44` - add `self._connector = None` after `await self._connector.close()`
- `channel/telegram/client.py:43` - same fix needed

### 3. Type Annotation Improvements

**Decision**: Add specific type annotations where `Any` is used unnecessarily.

**Rationale**: Better type safety and IDE support. Some uses of `Any` are acceptable (e.g., exception handling in `__aexit__`), but others can be improved.

**Files Affected**:
- `session/runner.py:392` - `process_streaming_request` should return `AsyncGenerator[str] | dict[str, Any]`
- `session/runner.py:542` - `_make_streaming_response` should return `AsyncGenerator[str]`

### 4. Test Function Type Annotations

**Decision**: Add return type annotations to test functions for consistency.

**Rationale**: While pytest test functions don't require return types, adding them improves consistency with the codebase standards.

**Files Affected**: Multiple test files have async test functions without `-> None` annotations.

### 5. Docstring Improvements

**Decision**: Add `Raises` sections to functions that can raise exceptions.

**Rationale**: Complete documentation helps users understand error conditions.

**Files Affected**:
- `session/tool_loader.py:load_tool_from_file` - can raise various exceptions during import
- `session/runner.py:process_request` - can raise exceptions during tool execution

## Risks / Trade-offs

### Risk: Import reordering may cause subtle issues
**Mitigation**: Run full test suite after changes. Import order changes are cosmetic and shouldn't affect behavior, but circular imports could be revealed.

### Risk: Type annotation changes may introduce type errors
**Mitigation**: Run `ty check` after changes. If new errors appear, evaluate whether the annotation or the code needs fixing.

### Risk: Changes to async context managers could affect resource cleanup
**Mitigation**: The changes are additive (setting to `None` after cleanup), which is the correct pattern already used elsewhere in the codebase.

## Migration Plan

1. **Phase 1**: Fix import order violations (automated via `ruff format`)
2. **Phase 2**: Fix async context manager pattern in channel clients
3. **Phase 3**: Add type annotations to session runner
4. **Phase 4**: Add docstring improvements
5. **Phase 5**: Run full quality check (`ruff check`, `ruff format`, `ty check`, `pytest`)

Each phase should be committed separately for easier review and rollback if needed.
