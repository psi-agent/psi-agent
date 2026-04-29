## Why

The `auto-alpha-tag.yml` workflow creates alpha tags daily for CI-passed commits, but the `publish` job in `ci.yml` is not triggered because GitHub's internal `GITHUB_TOKEN` cannot trigger other workflow runs. This means alpha tags are created but never published to PyPI, breaking the automated release pipeline.

## What Changes

- Copy the `publish` job from `ci.yml` into `auto-alpha-tag.yml` as a new job that runs after `auto-tag` job
- The new job will run when a new tag is successfully created by the `auto-tag` job
- Remove the `if: startsWith(github.ref, 'refs/tags/v')` condition since the workflow itself is only triggered by the auto-tag process

## Capabilities

### New Capabilities

- `auto-alpha-publish`: Automated PyPI publishing for alpha tags created by the auto-alpha-tag workflow

### Modified Capabilities

None - this is a new capability, not a modification to existing behavior.

## Impact

- `.github/workflows/auto-alpha-tag.yml` - add `publish` job
- PyPI package publishing will happen automatically after alpha tag creation