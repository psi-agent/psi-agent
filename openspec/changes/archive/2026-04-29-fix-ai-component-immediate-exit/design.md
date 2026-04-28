## Context

During the recent CLI refactor to support `psi-agent` as a unified entry point, all standalone CLI entry points were updated to use tyro. However, a critical bug was introduced: `tyro.cli()` returns a callable dataclass instance, but the standalone `main()` functions never call it.

The unified CLI in `__main__.py` works correctly because it explicitly calls the result:
```python
result = tyro.cli(top_commands, prog_name="psi-agent")
result()  # <-- This call is present
```

But all standalone entry points defined in `pyproject.toml` are missing this call:
```python
def main() -> None:
    tyro.cli(SomeCommand)  # <-- Missing () to call the result
```

## Goals / Non-Goals

**Goals:**
- Fix all 11 standalone CLI entry points to call the returned object
- Ensure backward compatibility - existing command-line usage should work as before
- Minimal code change - single line fix per file

**Non-Goals:**
- Refactoring CLI structure
- Adding new features
- Changing the unified `psi-agent` CLI (it already works)

## Decisions

### Decision 1: Add `()` call to each `main()` function

**Rationale:** This is the simplest and most direct fix. It matches the pattern used in `__main__.py` which already works correctly.

**Alternatives considered:**
- Use `tyro.cli(..., call=True)` - tyro doesn't support this parameter
- Change `main()` to return the callable and let the entry point call it - more complex, changes semantics

**Chosen approach:** Add `()` after each `tyro.cli()` call:
```python
def main() -> None:
    tyro.cli(SomeCommand)()
```

## Risks / Trade-offs

- **Risk: Tests may need updates** → Mitigation: Run existing tests after fix, update if needed
- **Risk: Behavior change visible to users** → Mitigation: This restores expected behavior, not a breaking change