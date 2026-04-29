## 1. Modify auto-alpha-tag.yml

- [x] 1.1 Add job output from `auto-tag` job to indicate if a new tag was created
- [x] 1.2 Add `publish` job with `needs: [auto-tag]` dependency
- [x] 1.3 Configure `publish` job to run only when a new tag was created
- [x] 1.4 Copy the publish steps from `ci.yml` (checkout, setup uv, build, publish)
- [x] 1.5 Add `environment: pypi` and `permissions: id-token: write` to `publish` job

## 2. Verification

- [x] 2.1 Verify workflow syntax is valid
- [x] 2.2 Review the complete workflow to ensure all requirements are met