## Why

CI fails because `ty` type checker is not installed. The workflow runs `uv run ty check` but `ty` is not listed in dev dependencies, causing the command to fail with "No such file or directory".

## What Changes

- Add `ty` to dev dependencies in pyproject.toml

## Capabilities

### New Capabilities

<!-- No new capabilities - this is a dependency fix -->

### Modified Capabilities

<!-- No spec-level requirement changes -->

## Impact

- pyproject.toml: dev dependencies updated
- CI workflow will now pass the type check step