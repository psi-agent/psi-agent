## ADDED Requirements

### Requirement: Snapshot creates layer from mounted workspace

The snapshot API SHALL create a new layer from the current state of a mounted workspace.

#### Scenario: Successful snapshot creation
- **WHEN** snapshot is called with valid squashfs path and mount point
- **THEN** a new layer SHALL be created with the current workspace state
- **AND** manifest.json SHALL be updated with the new layer

#### Scenario: Snapshot with tag
- **WHEN** snapshot is called with a tag parameter
- **THEN** the new layer SHALL include the tag in manifest.json

### Requirement: Snapshot validates inputs

The snapshot API SHALL validate input parameters before execution.

#### Scenario: Invalid squashfs path
- **WHEN** snapshot is called with non-existent squashfs file
- **THEN** an appropriate error SHALL be raised

#### Scenario: Invalid mount point
- **WHEN** snapshot is called with non-existent mount point
- **THEN** an appropriate error SHALL be raised

### Requirement: Snapshot handles errors gracefully

The snapshot API SHALL handle errors gracefully and provide meaningful error messages.

#### Scenario: Permission denied
- **WHEN** snapshot operation fails due to insufficient permissions
- **THEN** a clear error message SHALL be returned indicating permission issue

#### Scenario: Disk space insufficient
- **WHEN** snapshot operation fails due to insufficient disk space
- **THEN** a clear error message SHALL be returned indicating space issue
