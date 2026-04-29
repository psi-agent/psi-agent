## Purpose

Define the CI workflow requirements for automated code quality checks and testing.
## Requirements
### Requirement: CI runs on any push and pull request

The CI workflow SHALL run on every push to any branch, and on every pull request.

#### Scenario: Push to any branch triggers CI
- **WHEN** a commit is pushed to any branch
- **THEN** the CI workflow runs lint, format check, type check, and tests

#### Scenario: Any pull request triggers CI
- **WHEN** a pull request is opened or updated
- **THEN** the CI workflow runs lint, format check, type check, and tests

### Requirement: CI runs ruff lint check

The CI workflow SHALL run `ruff check` to verify code style compliance.

#### Scenario: Lint passes on valid code
- **WHEN** the code follows ruff lint rules
- **THEN** the lint check step succeeds

#### Scenario: Lint fails on violations
- **WHEN** the code has lint violations
- **THEN** the lint check step fails with error details

### Requirement: CI runs ruff format check

The CI workflow SHALL run `ruff format --check` to verify code formatting.

#### Scenario: Format passes on properly formatted code
- **WHEN** all files are formatted according to ruff rules
- **THEN** the format check step succeeds

#### Scenario: Format fails on unformatted code
- **WHEN** files are not properly formatted
- **THEN** the format check step fails showing files needing formatting

### Requirement: CI runs type checking

The CI workflow SHALL run `ty check` for type verification.

#### Scenario: Type check passes on correctly typed code
- **WHEN** all type annotations are correct
- **THEN** the type check step succeeds

### Requirement: CI runs pytest

The CI workflow SHALL run `pytest` to execute all tests.

#### Scenario: Tests pass when all tests succeed
- **WHEN** all test cases pass
- **THEN** the test step succeeds

#### Scenario: Tests fail on test failures
- **WHEN** any test case fails
- **THEN** the test step fails with failure details

### Requirement: CI uses uv for Python setup

The CI workflow SHALL use `uv` for Python environment setup and dependency installation.

#### Scenario: uv installs dependencies correctly
- **WHEN** the CI workflow starts
- **THEN** uv installs Python 3.14 and all dependencies from pyproject.toml

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

### Requirement: Test step generates JUnit XML

The CI workflow SHALL run pytest with JUnit XML output.

#### Scenario: JUnit XML generation
- **WHEN** the test step runs
- **THEN** pytest executes with `--junitxml=junit.xml -o junit_family=legacy`
- **AND** junit.xml is generated in the project root

