## 1. Fix typing issues in session module

- [x] 1.1 Add `cast()` for croniter return type in `schedule.py`
- [x] 1.2 Fix `response.prepare()` call in `server.py` to pass correct request object

## 2. Fix E402 violations in CLI __init__.py files

- [x] 2.1 Refactor `psi_agent/ai/__init__.py` to use `if TYPE_CHECKING:` pattern
- [x] 2.2 Refactor `psi_agent/workspace/__init__.py` to use `if TYPE_CHECKING:` pattern
- [x] 2.3 Refactor `psi_agent/channel/__init__.py` to use `if TYPE_CHECKING:` pattern

## 3. Remove global ignore rule from pyproject.toml

- [x] 3.1 Remove `no-matching-overload = "ignore"` from `[tool.ty.rules]` in `pyproject.toml`

## 4. Verify all checks pass

- [x] 4.1 Run `ruff check src/` and verify all checks pass
- [x] 4.2 Run `ty check src/` and verify all checks pass
- [x] 4.3 Run `pytest` and verify all tests pass
- [x] 4.4 Test CLI commands work correctly
