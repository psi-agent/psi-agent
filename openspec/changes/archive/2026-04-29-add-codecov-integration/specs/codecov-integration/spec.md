## ADDED Requirements

### Requirement: Coverage report upload to Codecov

The CI workflow SHALL upload coverage reports to Codecov after test execution.

#### Scenario: Successful coverage upload on PR
- **WHEN** a pull request is opened or updated
- **THEN** the CI uploads coverage.xml to Codecov
- **AND** the PR shows coverage change percentage

#### Scenario: Successful coverage upload on push to main
- **WHEN** code is pushed to main branch
- **THEN** the CI uploads coverage.xml to Codecov
- **AND** Codecov updates coverage history

### Requirement: Coverage report format

The CI workflow SHALL generate coverage reports in XML (Cobertura) format.

#### Scenario: XML report generation
- **WHEN** pytest runs with coverage
- **THEN** coverage.xml file is generated in the project root
- **AND** the report includes line-by-line coverage data

### Requirement: Non-blocking Codecov failures

Codecov upload failures SHALL NOT cause CI failure.

#### Scenario: Codecov service unavailable
- **WHEN** Codecov service is temporarily unavailable
- **THEN** the CI continues without error
- **AND** the workflow completes successfully

Note: This is achieved by using Codecov action's default behavior.
