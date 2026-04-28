## Context

The codebase currently has several ignored lint and typing errors:

1. **pyproject.toml**: `no-matching-overload = "ignore"` - a global ty rule ignore
2. **schedule.py:47**: `# type: ignore[no-any-return]` - croniter's `get_next()` returns `Any`
3. **server.py:126**: `# type: ignore` - incorrect `request` parameter passed to `response.prepare()`
4. **Multiple `__init__.py` files**: `# noqa: E402` for module-level imports after class definitions

These ignores represent technical debt that can be resolved with straightforward code changes.

## Goals / Non-Goals

**Goals:**
- Remove all unnecessary type ignore comments
- Remove the `no-matching-overload` ignore rule from pyproject.toml
- Restructure CLI `__init__.py` files to avoid E402 violations
- Maintain 100% backward compatibility

**Non-Goals:**
- Fixing third-party library typing issues (croniter's typing is external)
- Major architectural changes
- Adding new features

## Decisions

### Decision 1: Use `cast()` for croniter return type

**Rationale:** The `croniter` library's `get_next()` method returns `Any` because it can return different types based on the `ret_type` parameter. Since we always pass `datetime` as the return type, we can safely use `typing.cast()` to inform the type checker of the actual return type.

**Alternative considered:** Keep the ignore. Rejected because it masks a solvable typing issue.

### Decision 2: Remove incorrect `request` parameter in `response.prepare()`

**Rationale:** The `aiohttp` `StreamResponse.prepare()` method requires a `BaseRequest` object, not the `web.Request` class. The correct approach is to pass the actual `request` parameter from the handler method, not the class itself.

**Alternative considered:** Keep the ignore. Rejected because the code is actually incorrect - it passes the wrong object.

### Decision 3: Use `if TYPE_CHECKING:` pattern for CLI imports

**Rationale:** The E402 violations occur because we import CLI classes after defining the `Commands` dataclass that uses them. The Pythonic solution is to use `if TYPE_CHECKING:` blocks for type annotations and import the actual classes inside the `__call__` method.

**Alternative considered:** Keep `# noqa: E402`. Rejected because it's a lint violation that can be fixed properly.

## Risks / Trade-offs

- **Risk:** `cast()` provides no runtime type safety
  - **Mitigation:** The cast is correct because we control the `ret_type=datetime` parameter

- **Risk:** Changing import structure might affect import-time side effects
  - **Mitigation:** The CLI classes have no import-time side effects; they're only instantiated when `__call__` is invoked
