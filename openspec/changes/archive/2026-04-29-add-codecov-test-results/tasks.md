## 1. Modify Test Command

- [x] 1.1 Update pytest command to generate JUnit XML (`--junitxml=junit.xml -o junit_family=legacy`)
- [x] 1.2 Verify junit.xml is generated correctly

## 2. Add Codecov Test Results Action

- [x] 2.1 Add `codecov/test-results-action@v1` step after test step in ci.yml
- [x] 2.2 Configure action with `token` and `if: ${{ !cancelled() }}`

## 3. Update .gitignore

- [x] 3.1 Add junit.xml to .gitignore

## 4. Verify Integration

- [ ] 4.1 Push changes and verify CI passes
- [ ] 4.2 Check PR shows Codecov test results
