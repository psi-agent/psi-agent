## Context

The CLI modules use tyro for argument parsing. Tyro automatically generates negation flags for boolean parameters:
- `no_stream: bool = False` produces `--no-stream` (to set True) and `--no-no-stream` (to set False)

This is confusing because:
1. `--no-no-stream` is double-negative and unintuitive
2. The parameter name `no_stream` suggests "disable streaming" but the default `False` means streaming is enabled

The fix is straightforward: rename to `stream: bool = True`, which produces:
- `--stream` (explicitly enable, though it's already the default)
- `--no-stream` (disable streaming)

## Goals / Non-Goals

**Goals:**
- Rename CLI parameter from `no_stream` to `stream` with inverted default value
- Produce intuitive CLI flags: `--stream` (default) and `--no-stream` (disable)
- Maintain backward compatibility in internal APIs (config objects already use `stream`)

**Non-Goals:**
- Changing the underlying streaming behavior
- Modifying config classes (they already use `stream` parameter correctly)
- Adding new streaming-related features

## Decisions

### Decision 1: Parameter rename with inverted default

**Choice**: Rename `no_stream: bool = False` to `stream: bool = True`

**Rationale**:
- Produces clean CLI flags: `--stream` / `--no-stream`
- Matches the internal config objects which already use `stream` parameter
- Positive naming is more intuitive than negative naming

**Alternatives considered**:
1. Keep `no_stream` but change default to `True` - would make `--no-stream` the default flag, still confusing
2. Use custom CLI parsing to override tyro's negation handling - adds complexity for a simple rename

### Decision 2: Update all test assertions

**Choice**: Update all test files to use `stream` parameter directly

**Rationale**:
- Tests should reflect the actual API
- No value in maintaining backward compatibility in test code
- Simpler assertions: `assert cli.stream is True` vs `assert cli.no_stream is False`

## Risks / Trade-offs

**Risk**: Users who have scripts using `--no-stream` will see different behavior
→ **Mitigation**: This is technically a breaking change, but the previous `--no-stream` flag was setting `no_stream=True` (disabling streaming). After the change, `--no-stream` will still disable streaming. The behavior is identical, only the internal parameter name changes.

**Risk**: Documentation may reference `no_stream` parameter
→ **Mitigation**: Review and update any documentation. Based on codebase search, the parameter is only documented in docstrings which will be updated.
