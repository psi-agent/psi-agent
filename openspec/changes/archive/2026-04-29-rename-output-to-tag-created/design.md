## Context

Simple naming consistency fix. The `auto-alpha-tag.yml` workflow has two outputs from the `create-tag` step:
- `created` - boolean indicating if a tag was created
- `tag-name` - the name of the created tag

The naming is inconsistent: `tag-name` uses kebab-case prefix while `created` does not.

## Goals / Non-Goals

**Goals:**
- Rename `created` to `tag-created` for consistent naming with `tag-name`

**Non-Goals:**
- Any behavior changes
- Other workflow modifications

## Decisions

**Decision: Use `tag-created` as the new name**

This matches the pattern of `tag-name` and makes the output names self-documenting.

## Risks / Trade-offs

None - this is a simple rename with no functional impact.
