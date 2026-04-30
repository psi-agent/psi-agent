## ADDED Requirements

### Requirement: Mount creates overlayfs from squashfs

The mount API SHALL create an overlayfs mount from a squashfs image.

#### Scenario: Successful mount
- **WHEN** mount is called with valid squashfs path and output directory
- **THEN** an overlayfs SHALL be created at the output directory
- **AND** the workspace content SHALL be accessible

#### Scenario: Mount specific layer
- **WHEN** mount is called with a layer tag
- **THEN** the specified layer SHALL be mounted instead of the default

### Requirement: Mount validates inputs

The mount API SHALL validate input parameters before execution.

#### Scenario: Invalid squashfs path
- **WHEN** mount is called with non-existent squashfs file
- **THEN** an appropriate error SHALL be raised

#### Scenario: Output directory exists
- **WHEN** mount is called with an existing output directory
- **THEN** an appropriate error SHALL be raised to prevent overwriting

### Requirement: Mount handles errors gracefully

The mount API SHALL handle errors gracefully and provide meaningful error messages.

#### Scenario: Permission denied
- **WHEN** mount operation fails due to insufficient permissions
- **THEN** a clear error message SHALL be returned indicating root permission requirement

#### Scenario: Invalid squashfs format
- **WHEN** mount is called with a corrupted or invalid squashfs file
- **THEN** a clear error message SHALL be returned indicating format issue
