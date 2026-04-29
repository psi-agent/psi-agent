## 1. Rename output in workflow

- [x] 1.1 Rename `created` to `tag-created` in the step output (`echo "created=true" >> $GITHUB_OUTPUT`)
- [x] 1.2 Rename `created` to `tag-created` in the job outputs mapping
- [x] 1.3 Rename `created` to `tag-created` in the publish job's `if` condition

## 2. Update spec

- [x] 2.1 Update `openspec/specs/auto-alpha-publish/spec.md` to reflect the new output name