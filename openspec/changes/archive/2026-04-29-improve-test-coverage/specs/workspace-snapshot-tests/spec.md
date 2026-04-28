## ADDED Requirements

### Requirement: Snapshot creation
The snapshot API SHALL create new workspace layers from mounted overlayfs.

#### Scenario: Create snapshot with tag
- **WHEN** snapshot is created with a tag
- **THEN** new layer is added to manifest with the tag

#### Scenario: Create snapshot without tag
- **WHEN** snapshot is created without tag
- **THEN** new layer is added with auto-generated UUID

### Requirement: Layer management
The snapshot API SHALL properly manage layer hierarchy.

#### Scenario: Layer parent relationship
- **WHEN** snapshot is created
- **THEN** new layer has correct parent reference

#### Scenario: Default layer update
- **WHEN** snapshot is created
- **THEN** manifest default is updated to new layer

### Requirement: Error handling
The snapshot API SHALL handle errors gracefully.

#### Scenario: Invalid mount point
- **WHEN** snapshot is requested for invalid mount
- **THEN** appropriate error is raised

#### Scenario: Insufficient permissions
- **WHEN** snapshot is requested without root
- **THEN** permission error is raised