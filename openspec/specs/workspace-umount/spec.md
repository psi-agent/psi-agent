## ADDED Requirements

### Requirement: Umount cleanly removes overlayfs
The system SHALL unmount the overlayfs and clean up temporary resources.

#### Scenario: Umount mounted workspace
- **WHEN** user runs `psi-workspace-umount --output ./mounted-workspace`
- **THEN** system unmounts the overlayfs from the output path
- **AND** system unmounts the squashfs from the temporary directory
- **AND** system removes the temporary upper and work directories
- **AND** system removes the temporary squashfs mount directory

### Requirement: Umount validates mount point
The system SHALL validate the specified path is a valid overlayfs mount.

#### Scenario: Invalid mount point
- **WHEN** user specifies a path that is not an overlayfs mount
- **THEN** system raises an exception with a clear error message

### Requirement: Umount handles partial cleanup
The system SHALL attempt cleanup even if unmount fails.

#### Scenario: Unmount failure with cleanup
- **WHEN** overlayfs unmount fails
- **THEN** system logs the error
- **AND** system still attempts to clean up temporary directories
- **AND** system raises an exception with both errors

### Requirement: Umount uses async operations
The system SHALL use async operations where possible.

#### Scenario: Async cleanup operations
- **WHEN** umount is running
- **THEN** directory removal uses async methods
- **AND** unmount system calls are executed via async subprocess