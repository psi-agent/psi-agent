## MODIFIED Requirements

### Requirement: Skip already-tagged commits
The workflow SHALL NOT create a tag if the target commit already has any tag (including both lightweight and annotated tags).

#### Scenario: Commit has existing lightweight tag
- **WHEN** the identified commit already has a lightweight tag
- **THEN** the workflow exits without creating a new tag

#### Scenario: Commit has existing annotated tag
- **WHEN** the identified commit already has an annotated tag
- **THEN** the workflow exits without creating a new tag

#### Scenario: Commit has no tag
- **WHEN** the identified commit has no existing tag
- **THEN** the workflow proceeds to create a new alpha tag
