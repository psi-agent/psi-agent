## ADDED Requirements

### Requirement: Unmount workspace
The umount API SHALL properly unmount overlayfs mounts.

#### Scenario: Unmount valid mount
- **WHEN** umount is called on valid mount point
- **THEN** overlayfs is unmounted and directories cleaned

#### Scenario: Unmount non-existent mount
- **WHEN** umount is called on non-mounted directory
- **THEN** appropriate error is raised

### Requirement: Cleanup operations
The umount API SHALL clean up temporary directories.

#### Scenario: Clean work directory
- **WHEN** umount completes
- **THEN** work directory is removed

#### Scenario: Handle partial cleanup
- **WHEN** some cleanup steps fail
- **THEN** remaining cleanup continues

### Requirement: Permission handling
The umount API SHALL require root permissions.

#### Scenario: Run without root
- **WHEN** umount is called without root
- **THEN** permission error is raised