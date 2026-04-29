## 1. Workflow File Creation

- [x] 1.1 Create `.github/workflows/auto-alpha-tag.yml` file with workflow structure
- [x] 1.2 Configure workflow triggers (schedule at 1:00 UTC and workflow_dispatch)
- [x] 1.3 Set workflow permissions (`contents: write`)

## 2. Find Last CI-Passed Commit

- [x] 2.1 Add step to checkout repository
- [x] 2.2 Add step to install GitHub CLI (gh)
- [x] 2.3 Add step to query last successful CI.yml run on main branch
- [x] 2.4 Add step to extract commit SHA from the run
- [x] 2.5 Add error handling for no successful runs found

## 3. Check Existing Tags

- [x] 3.1 Add step to fetch all tags from remote
- [x] 3.2 Add step to check if commit already has a tag using `git describe --exact-match`
- [x] 3.3 Add conditional to skip workflow if commit is already tagged

## 4. Derive Version from Previous Alpha Tag

- [x] 4.1 Add step to list all alpha tags sorted by creation date
- [x] 4.2 Add step to extract version prefix (N.N.N) from most recent alpha tag
- [x] 4.3 Add error handling for no previous alpha tag found

## 5. Create and Push Tag

- [x] 5.1 Add step to generate date suffix (YYYYMMDD format)
- [x] 5.2 Add step to construct full tag name (N.N.N-alphaYYYYMMDD)
- [x] 5.3 Add step to check if tag with same date suffix already exists
- [x] 5.4 Add step to create the tag on the commit
- [x] 5.5 Add step to push the tag to origin repository

## 6. Verification

- [ ] 6.1 Test workflow manually via workflow_dispatch
- [ ] 6.2 Verify workflow logs show correct behavior for all scenarios
- [ ] 6.3 Verify created tags appear in repository