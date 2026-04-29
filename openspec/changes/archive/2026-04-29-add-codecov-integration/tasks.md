## 1. Modify Test Coverage Command

- [x] 1.1 Update pytest command to generate XML coverage report (`--cov-report=xml --cov-branch`)
- [x] 1.2 Verify coverage.xml is generated in project root with branch coverage

## 2. Add Codecov Action

- [x] 2.1 Add `codecov/codecov-action@v5` step after test step in ci.yml
- [x] 2.2 Configure action with token and slug (using Codecov defaults)

## 3. Update .gitignore

- [x] 3.1 Add coverage.xml to .gitignore

## 4. Verify Integration

- [ ] 4.1 Push changes and verify CI passes
- [ ] 4.2 Check PR shows Codecov bot comment with coverage change
