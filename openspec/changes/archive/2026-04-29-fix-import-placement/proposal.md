## Why

Test files had imports placed inside function bodies, violating CLAUDE.md's import order specification. This makes code harder to read and goes against Python best practices.

## What Changes

- Move all imports from function bodies to file headers in test files
- Ensure import order follows: stdlib → third-party → local

## Capabilities

### New Capabilities

- `import-placement`: All imports SHALL be placed at file header, following the order: stdlib → third-party → local

### Modified Capabilities

- None

## Impact

- Test files in `tests/` directory
- No API or runtime behavior changes
