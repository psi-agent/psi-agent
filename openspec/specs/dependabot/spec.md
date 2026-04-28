## ADDED Requirements

### Requirement: Dependabot checks uv dependencies

Dependabot SHALL check Python dependencies using the uv ecosystem, monitoring pyproject.toml and uv.lock.

#### Scenario: Python dependency update available
- **WHEN** a Python dependency has a new version available
- **THEN** Dependabot creates a PR updating the dependency

### Requirement: Dependabot checks GitHub Actions

Dependabot SHALL check GitHub Actions workflows for action version updates.

#### Scenario: GitHub Action update available
- **WHEN** a GitHub Action has a new version available
- **THEN** Dependabot creates a PR updating the action version

### Requirement: Dependabot runs weekly

Dependabot SHALL check for updates on a weekly schedule.

#### Scenario: Weekly schedule triggers checks
- **WHEN** the weekly schedule time arrives
- **THEN** Dependabot checks all configured ecosystems for updates

### Requirement: Dependabot limits open PRs

Dependabot SHALL limit the number of open PRs to prevent excessive noise.

#### Scenario: PR limit prevents excessive updates
- **WHEN** multiple updates are available
- **THEN** Dependabot creates at most the configured limit of open PRs

### Requirement: Dependabot groups minor updates

Dependabot SHALL group minor and patch updates together to reduce PR volume.

#### Scenario: Minor updates grouped together
- **WHEN** multiple dependencies have minor/patch updates
- **THEN** Dependabot creates a single grouped PR instead of individual PRs