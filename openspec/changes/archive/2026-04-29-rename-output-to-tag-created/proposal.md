## Why

The `auto-alpha-tag.yml` workflow uses inconsistent output naming: `steps.create-tag.outputs.created` for the boolean flag but `steps.create-tag.outputs.tag-name` for the tag name. This inconsistency reduces code readability.

## What Changes

- Rename `created` output to `tag-created` for consistency with `tag-name`

## Capabilities

### New Capabilities

None

### Modified Capabilities

- `auto-alpha-publish`: Output naming convention change (no behavior change)

## Impact

- `.github/workflows/auto-alpha-tag.yml` - rename output from `created` to `tag-created`
- `openspec/specs/auto-alpha-publish/spec.md` - update to reflect new output name