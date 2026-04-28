## Why

The dev/coverage branch needs to be rebased onto origin/main to incorporate recent changes. Additionally, there are linting issues (line too long, unused imports, unsorted imports) that need to be fixed to pass CI checks.

## What Changes

- Rebase dev/coverage branch onto origin/main
- Fix E501 (line too long) errors in test files
- Fix F401 (unused import) error in test_snapshot.py
- Fix I001 (unsorted imports) error in test_snapshot.py

## Capabilities

### New Capabilities
- None (this is a maintenance task)

### Modified Capabilities
- None (no spec-level behavior changes)

## Impact

- Test files only (no production code changes)
- CI will pass after fixes
