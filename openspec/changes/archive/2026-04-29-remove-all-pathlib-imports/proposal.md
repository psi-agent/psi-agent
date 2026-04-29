## Why

The codebase still imports `pathlib.Path` as `SyncPath` in test files for type annotations on pytest's `tmp_path` fixture. This is unnecessary - we can use `anyio.Path` directly in function bodies by converting `tmp_path` immediately upon use. This eliminates the last remaining `pathlib` imports and ensures consistency across the entire codebase.

## What Changes

- Remove all `from pathlib import Path as SyncPath` imports from test files
- Change fixture type annotations from `SyncPath` to `anyio.Path`
- Convert `tmp_path` to `anyio.Path` immediately in test function bodies where needed

## Capabilities

### New Capabilities

None - this is a cleanup change with no new capabilities.

### Modified Capabilities

- `platform-cache-dirs`: Update the requirement to remove the exception for test files - no `pathlib.Path` imports anywhere in the codebase.

## Impact

- **Affected Code**: All test files in `tests/` directory (12 files)
- **Behavior**: No behavior change - only internal implementation cleanup
- **Dependencies**: None
