## ADDED Requirements

### Requirement: Daily scheduled execution
The workflow SHALL execute daily at 9:00 AM Beijing time (UTC+8).

#### Scenario: Scheduled trigger fires correctly
- **WHEN** the cron schedule reaches 1:00 UTC (9:00 AM Beijing)
- **THEN** the workflow is triggered automatically

### Requirement: Find last CI-passed commit
The workflow SHALL identify the most recent commit on main branch that has passed the CI.yml workflow.

#### Scenario: CI-passed commit found
- **WHEN** there is at least one successful CI.yml run on main branch
- **THEN** the workflow identifies the head SHA of the most recent successful run

#### Scenario: No CI-passed commit exists
- **WHEN** there are no successful CI.yml runs on main branch
- **THEN** the workflow exits gracefully without creating a tag

### Requirement: Skip already-tagged commits
The workflow SHALL NOT create a tag if the target commit already has any tag.

#### Scenario: Commit has existing tag
- **WHEN** the identified commit already has a tag
- **THEN** the workflow exits without creating a new tag

#### Scenario: Commit has no tag
- **WHEN** the identified commit has no existing tag
- **THEN** the workflow proceeds to create a new alpha tag

### Requirement: Derive tag version from previous alpha tag
The workflow SHALL derive the version prefix (N.N.N) from the most recent existing alpha tag.

#### Scenario: Previous alpha tag found
- **WHEN** there is at least one tag matching pattern `*-alpha*`
- **THEN** the workflow extracts the version prefix (N.N.N) from the most recent one

#### Scenario: No previous alpha tag exists
- **WHEN** there are no tags matching pattern `*-alpha*`
- **THEN** the workflow fails with an error message requiring manual initial tag creation

### Requirement: Create alpha tag with date suffix
The workflow SHALL create a tag with format `vN.N.N-alphaYYYYMMDD` where YYYYMMDD is the current date.

#### Scenario: Tag created successfully
- **WHEN** all prerequisites are satisfied (commit found, no existing tag, previous alpha tag exists)
- **THEN** a new tag `vN.N.N-alphaYYYYMMDD` is created on the commit

#### Scenario: Tag already exists for current date
- **WHEN** a tag with the same date suffix already exists
- **THEN** the workflow skips tag creation to avoid duplicates

### Requirement: Push tag to repository
The workflow SHALL push the created tag to the remote repository.

#### Scenario: Tag pushed successfully
- **WHEN** a new tag is created
- **THEN** the tag is pushed to the origin repository

### Requirement: Manual trigger support
The workflow SHALL support manual triggering via workflow_dispatch for testing purposes.

#### Scenario: Manual trigger
- **WHEN** user triggers the workflow manually via workflow_dispatch
- **THEN** the workflow executes the same logic as scheduled runs