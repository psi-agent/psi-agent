## ADDED Requirements

### Requirement: Snapshot creates atomic update
The system SHALL create a snapshot with atomic write to prevent data loss.

#### Scenario: Snapshot with atomic write
- **WHEN** user runs `psi-workspace-snapshot --input ./workspace.squashfs --mount-point ./mounted-workspace`
- **THEN** system copies the original squashfs to a temporary file in the same directory
- **AND** system adds the diff (upper directory) as a new UUID-named layer
- **AND** system updates the manifest.json with the new layer
- **AND** system moves the temporary file to the final location atomically

### Requirement: Snapshot supports custom output
The system SHALL allow users to specify a custom output path.

#### Scenario: Snapshot to new file
- **WHEN** user runs `psi-workspace-snapshot --input ./workspace.squashfs --mount-point ./mounted-workspace --output ./workspace-v2.squashfs`
- **THEN** system creates a new squashfs at the specified output path
- **AND** the original squashfs is not modified

### Requirement: Snapshot supports tag
The system SHALL allow users to specify a tag for the new layer.

#### Scenario: Snapshot with tag
- **WHEN** user runs `psi-workspace-snapshot --input ./workspace.squashfs --mount-point ./mounted-workspace --tag v1.1`
- **THEN** the new layer has tag "v1.1" in manifest.json
- **AND** the tag is unique across all layers

### Requirement: Snapshot updates manifest correctly
The system SHALL update manifest.json with the new layer information.

#### Scenario: Manifest update
- **WHEN** snapshot completes successfully
- **THEN** manifest.json contains a new layer entry with a UUID name
- **AND** the new layer has a `parent` field referencing the current default layer
- **AND** the `default` field is updated to the new layer UUID

### Requirement: Snapshot generates UUID for new layer
The system SHALL generate a UUID for the new layer.

#### Scenario: UUID generation
- **WHEN** snapshot creates a new layer
- **THEN** the layer name is a valid UUID v4
- **AND** the directory name in squashfs matches the UUID

### Requirement: Snapshot handles empty diff
The system SHALL handle cases where no changes were made.

#### Scenario: No changes in upper directory
- **WHEN** upper directory is empty (no modifications made)
- **THEN** system logs a warning that no changes were detected
- **AND** system still creates a snapshot (optional behavior)

### Requirement: Snapshot validates inputs
The system SHALL validate all inputs before snapshot.

#### Scenario: Invalid squashfs file
- **WHEN** user specifies a non-existent squashfs file
- **THEN** system raises an exception with a clear error message

#### Scenario: Invalid mount point
- **WHEN** user specifies a path that is not an overlayfs mount
- **THEN** system raises an exception with a clear error message

### Requirement: Snapshot uses async operations
The system SHALL use async operations where possible.

#### Scenario: Async snapshot operations
- **WHEN** snapshot is running
- **THEN** file operations use async methods
- **AND** squashfs creation uses async subprocess
