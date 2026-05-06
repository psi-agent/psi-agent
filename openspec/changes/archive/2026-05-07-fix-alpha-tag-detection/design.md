## Context

The `auto-alpha-tag.yml` workflow creates lightweight tags (`git tag "$NEW_TAG"`) on commits that pass CI. Before creating a tag, it checks whether the commit already has one using `git describe --exact-match "$COMMIT_SHA"`. However, `git describe` only considers **annotated tags** by default — it ignores lightweight tags. Since the workflow itself creates lightweight tags, the check always fails, and the workflow will attempt to re-tag already-tagged commits on every scheduled run.

## Goals / Non-Goals

**Goals:**
- Fix tag detection to correctly identify both lightweight and annotated tags on a commit
- Ensure the "skip already-tagged commits" behavior works reliably

**Non-Goals:**
- Changing the tag creation method from lightweight to annotated (that would be a separate concern)
- Modifying the tag naming scheme or version derivation logic

## Decisions

**Decision: Use `git tag --list --points-at` instead of `git describe --exact-match`**

`git tag --list --points-at "$COMMIT_SHA"` lists all tags (both lightweight and annotated) pointing at a given commit. This is the simplest and most reliable fix.

Alternatives considered:
- `git describe --exact-match --tags "$COMMIT_SHA"` — adds `--tags` flag to include lightweight tags. This works but `git describe` is designed for version derivation, not tag existence checks. It also has edge cases with `--match` patterns that could interfere.
- `git for-each-ref --points-at` — more powerful but overkill for a simple existence check.

`git tag --list --points-at` is the most direct and readable approach for "does this commit have any tags?"

## Risks / Trade-offs

- [Risk: `git tag --list --points-at` output could be empty string vs no output] → Check with `[ -n "$(git tag --list --points-at ...)" ]` which handles both cases.
- [Risk: A commit could have non-alpha tags that should not block alpha tagging] → The current spec says "skip if the commit has *any* tag", so this is consistent with existing behavior. If finer-grained control is needed later, that's a separate change.
