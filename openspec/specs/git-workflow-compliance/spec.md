# Git Workflow Compliance

## Requirements

### Requirement: OpenSpec changes must be committed to Git
All OpenSpec change directories (including archive) SHALL be committed to Git as part of the project history.

#### Scenario: Archive directory committed
- **WHEN** an OpenSpec change is archived
- **THEN** the archive directory `openspec/changes/archive/YYYY-MM-DD-<name>/` SHALL be committed to Git

#### Scenario: Archive directory not ignored
- **WHEN** checking `.gitignore`
- **THEN** `openspec/changes/archive/` SHALL NOT be in the ignore list

### Requirement: No direct commits to main branch
All changes SHALL be made on a feature branch and merged via pull request.

#### Scenario: Feature branch created
- **WHEN** starting work on a change
- **THEN** a new branch SHALL be created from main

#### Scenario: Changes merged via PR
- **WHEN** work on a feature branch is complete
- **THEN** changes SHALL be merged via a pull request, NOT by direct push to main

### Requirement: No direct push to main branch
Direct push to main branch SHALL be prohibited for all developers.

#### Scenario: Push to main rejected
- **WHEN** a developer attempts to push directly to main
- **THEN** the push SHALL be rejected by branch protection rules

#### Scenario: PR required for merge
- **WHEN** changes need to be merged to main
- **THEN** a pull request SHALL be created and approved before merge
