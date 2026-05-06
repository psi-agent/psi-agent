## 1. Fix tag detection logic

- [x] 1.1 Replace `git describe --exact-match "$COMMIT_SHA"` with `git tag --list --points-at "$COMMIT_SHA"` in `.github/workflows/auto-alpha-tag.yml` line 53, and update the surrounding conditional to check for non-empty output instead of exit code

## 2. Update spec

- [x] 2.1 Update `openspec/specs/auto-alpha-tag/spec.md` to clarify that tag detection covers both lightweight and annotated tags
