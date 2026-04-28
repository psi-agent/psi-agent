## 1. Fix telegram bot type issues

- [x] 1.1 Add `assert self._app is not None` before accessing `updater` in `start()`
- [x] 1.2 Add `assert self._app.updater is not None` before calling updater methods
- [x] 1.3 Remove `# ty: ignore` comments from `telegram/bot.py`

## 2. Fix E501 violation in examples

- [x] 2.1 Remove `# ruff: noqa: E501` from `examples/.../system.py`
- [x] 2.2 Split long lines to comply with line length limit

## 3. Fix E402 violation in tests

- [x] 3.1 Move `from pathlib import Path` to top of `test_cron.py`
- [x] 3.2 Remove `# noqa: E402` comment

## 4. Create tyro issue reproduction

- [x] 4.1 Create minimal reproduction script for tyro Union type issue
- [x] 4.2 Document the issue for submission to tyro repository

## 5. Verify all checks pass

- [x] 5.1 Run `ruff check` and verify no errors
- [x] 5.2 Run `ty check` and verify no errors (except tyro issue)
- [x] 5.3 Run `pytest` and verify all tests pass
