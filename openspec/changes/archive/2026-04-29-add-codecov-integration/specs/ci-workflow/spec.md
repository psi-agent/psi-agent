## ADDED Requirements

### Requirement: Test coverage step

The CI workflow SHALL run pytest with coverage and generate XML report with branch coverage.

#### Scenario: Coverage report generation
- **WHEN** the test step runs
- **THEN** pytest executes with `--cov-report=xml --cov=src/psi_agent --cov-branch`
- **AND** coverage.xml is generated with line and branch coverage data

#### Scenario: Coverage upload after tests
- **WHEN** tests complete successfully
- **THEN** coverage.xml is uploaded to Codecov
- **AND** upload failure does not fail the CI
