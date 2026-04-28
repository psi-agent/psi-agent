## Why

The `ty check` command fails with a type error in `src/psi_agent/__main__.py:37` because tyro's type annotations don't support Union of Annotated types. While the runtime works correctly, this blocks CI/CD pipelines that require type checking to pass.

## What Changes

- Add `# type: ignore[no-matching-overload]` comment to suppress the false positive type error
- No functional changes - this is purely a type checker workaround

## Capabilities

### New Capabilities

None

### Modified Capabilities

None - this is a type annotation fix with no spec-level behavior changes.

## Impact

- `src/psi_agent/__main__.py` - add type ignore comment on line 37
