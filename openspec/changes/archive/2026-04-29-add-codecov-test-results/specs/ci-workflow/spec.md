## ADDED Requirements

### Requirement: Test step generates JUnit XML

The CI workflow SHALL run pytest with JUnit XML output.

#### Scenario: JUnit XML generation
- **WHEN** the test step runs
- **THEN** pytest executes with `--junitxml=junit.xml -o junit_family=legacy`
- **AND** junit.xml is generated in the project root
