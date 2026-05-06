## Why

`auto-alpha-tag.yml` uses `git describe --exact-match` to check if a commit already has a tag, but this command only considers **annotated tags** by default. Since the workflow creates **lightweight tags** (`git tag "$NEW_TAG"` without `-a`), the detection always fails — the workflow never recognizes its own tags, causing it to attempt re-tagging already-tagged commits on every run.

## What Changes

- Fix the tag detection in `auto-alpha-tag.yml` to correctly detect both lightweight and annotated tags on a commit
- Update the existing spec for `auto-alpha-tag` to clarify that detection must cover all tag types

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `auto-alpha-tag`: The "skip already-tagged commits" requirement must explicitly cover both lightweight and annotated tags

## Impact

- `.github/workflows/auto-alpha-tag.yml` — tag detection logic (line 53)
- `openspec/specs/auto-alpha-tag/spec.md` — requirement clarification
