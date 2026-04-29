## 1. Audit and Detection

- [x] 1.1 Run `ruff check --select I` to identify import order violations
- [x] 1.2 Run `ty check` to identify type annotation issues
- [x] 1.3 Search for legacy type syntax (`Optional[`, `Union[`, `List[`, `Dict[`, `Tuple[`)
- [x] 1.4 Search for `pathlib.Path` usage in IO operations
- [x] 1.5 Check all `__init__.py` files for `__all__` exports
- [x] 1.6 Verify all CLI classes with sensitive params have masking

## 2. Fix `from __future__ import annotations` (if needed)

- [x] 2.1 Add missing `from __future__ import annotations` to any files that lack it

## 3. Fix Legacy Type Syntax

- [x] 3.1 Replace `Optional[X]` with `X | None` in all files
- [x] 3.2 Replace `Union[X, Y]` with `X | Y` in all files
- [x] 3.3 Replace `List[X]` with `list[X]` in all files
- [x] 3.4 Replace `Dict[K, V]` with `dict[K, V]` in all files
- [x] 3.5 Replace `Tuple[X, ...]` with `tuple[X, ...]` in all files
- [x] 3.6 Remove legacy `from typing import Optional, Union, List, Dict, Tuple` imports

## 4. Fix Import Order

- [x] 4.1 Run `ruff format --select I` to auto-fix import order
- [x] 4.2 Manually verify import groups are correctly separated

## 5. Fix pathlib.Path IO Operations (Critical)

- [x] 5.1 Identify all `pathlib.Path` IO method calls (`.read_text()`, `.write_text()`, `.exists()`, `.iterdir()`, etc.)
- [x] 5.2 Replace with `anyio.Path` async equivalents
- [x] 5.3 Ensure all calling functions are async

## 6. Fix Missing Type Annotations

- [x] 6.1 Add type annotations to functions missing them
- [x] 6.2 Ensure return types are annotated

## 7. Fix Docstrings

- [x] 7.1 Add module docstrings to files missing them
- [x] 7.2 Add/fix Google-style function docstrings
- [x] 7.3 Ensure Args, Returns, Raises sections are properly formatted

## 8. Fix __all__ Exports

- [x] 8.1 Add `__all__` to `__init__.py` files missing it
- [x] 8.2 Verify all exported names are listed

## 9. Fix CLI Sensitive Argument Masking

- [x] 9.1 Add `mask_sensitive_args()` call to CLI classes handling credentials

## 10. Verification

- [x] 10.1 Run `ruff check` to verify no lint errors
- [x] 10.2 Run `ruff format --check` to verify formatting
- [x] 10.3 Run `ty check` to verify type checking passes
- [x] 10.4 Run `pytest` to verify all tests pass
