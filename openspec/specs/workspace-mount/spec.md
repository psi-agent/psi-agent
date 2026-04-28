## ADDED Requirements

### Requirement: Mount creates overlayfs from squashfs
The system SHALL mount a squashfs image as an overlayfs to a target directory.

#### Scenario: Mount with default layer
- **WHEN** user runs `psi-workspace-mount --input ./workspace.squashfs --output ./mounted-workspace`
- **THEN** system mounts the squashfs to a temporary directory (read-only)
- **AND** system resolves the layer chain from manifest default
- **AND** system creates an overlayfs using the resolved layer chain
- **AND** system mounts the overlayfs to the user-specified output path
- **AND** the output path is writable

### Requirement: Mount supports UUID specification
The system SHALL allow users to specify a layer by UUID.

#### Scenario: Mount with UUID
- **WHEN** user runs `psi-workspace-mount --input ./workspace.squashfs --output ./mounted-workspace --layer <uuid>`
- **THEN** system resolves the layer chain from the specified UUID
- **AND** system creates an overlayfs using the resolved layer chain

### Requirement: Mount supports tag specification
The system SHALL allow users to specify a layer by tag.

#### Scenario: Mount with tag
- **WHEN** user runs `psi-workspace-mount --input ./workspace.squashfs --output ./mounted-workspace --layer v1.0`
- **THEN** system looks up the UUID for tag "v1.0"
- **AND** system resolves the layer chain from that UUID
- **AND** system creates an overlayfs using the resolved layer chain

### Requirement: Mount creates required directories
The system SHALL automatically create upper and work directories for overlayfs.

#### Scenario: Overlayfs directories created
- **WHEN** mount is executed
- **THEN** system creates a temporary upper directory for writes
- **AND** system creates a temporary work directory for overlayfs
- **AND** both directories are cleaned up on umount

### Requirement: Mount validates inputs
The system SHALL validate all inputs before mounting.

#### Scenario: Invalid squashfs file
- **WHEN** user specifies a non-existent squashfs file
- **THEN** system raises an exception with a clear error message

#### Scenario: Invalid UUID
- **WHEN** user specifies a UUID that does not exist in manifest
- **THEN** system raises an exception listing available UUIDs

#### Scenario: Invalid tag
- **WHEN** user specifies a tag that does not exist in manifest
- **THEN** system raises an exception listing available tags

### Requirement: Mount requires root privileges
The system SHALL require appropriate privileges for mount operations.

#### Scenario: Insufficient privileges
- **WHEN** mount is executed without sufficient privileges
- **THEN** system raises an exception indicating privilege requirement

### Requirement: Mount uses async operations
The system SHALL use async operations where possible.

#### Scenario: Async setup operations
- **WHEN** mount is running
- **THEN** directory creation and validation use async methods
- **AND** mount system calls are executed via async subprocess
