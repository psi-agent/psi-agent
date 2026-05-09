## ADDED Requirements

### Requirement: Pack handles mksquashfs failure
`pack` SHALL raise `PackError` when the `mksquashfs` command fails.

#### Scenario: mksquashfs returns non-zero exit code
- **WHEN** `mksquashfs` command exits with a non-zero code
- **THEN** `PackError` SHALL be raised with an appropriate message

### Requirement: Pack handles empty input directory
`pack` SHALL handle an empty input directory without error.

#### Scenario: Empty directory
- **WHEN** `pack` is called with an empty directory
- **THEN** a squashfs file SHALL be created successfully

### Requirement: Unpack handles unsquashfs failure
`unpack` SHALL raise `UnpackError` when the `unsquashfs` command fails.

#### Scenario: Corrupt squashfs file
- **WHEN** `unpack` is called with a corrupt or invalid squashfs file
- **THEN** `UnpackError` SHALL be raised

#### Scenario: Empty squashfs file
- **WHEN** `unpack` is called with a 0-byte file
- **THEN** `UnpackError` SHALL be raised

### Requirement: Unpack handles output directory that already exists
`unpack` SHALL handle the case where the output directory already exists.

#### Scenario: Output directory exists
- **WHEN** `unpack` is called and the output directory already exists
- **THEN** the contents SHALL be extracted into the existing directory

### Requirement: Umount handles mount info with missing keys
`umount` SHALL raise `UmountError` when mount info dict is missing required keys (squashfs_mount, upper_dir, work_dir).

#### Scenario: Missing squashfs_mount key
- **WHEN** mount info dict lacks the `squashfs_mount` key
- **THEN** `UmountError` SHALL be raised (not `KeyError`)

#### Scenario: Missing upper_dir key
- **WHEN** mount info dict lacks the `upper_dir` key
- **THEN** `UmountError` SHALL be raised (not `KeyError`)

### Requirement: Umount _cleanup_directory handles read-only files
`_cleanup_directory` SHALL handle files that cannot be deleted due to permission errors.

#### Scenario: Read-only file in directory
- **WHEN** a directory contains a read-only file
- **THEN** the error SHALL be logged and the cleanup SHALL continue

### Requirement: Snapshot handles mount info with missing keys
`snapshot` SHALL raise `SnapshotError` when mount info dict is missing required keys.

#### Scenario: Missing upper_dir key in mount info
- **WHEN** mount info dict lacks the `upper_dir` key
- **THEN** `SnapshotError` SHALL be raised (not `KeyError`)

### Requirement: Snapshot handles output_file parameter
`snapshot` SHALL correctly handle the `output_file` parameter when it differs from `input_file`.

#### Scenario: Different output_file from input_file
- **WHEN** `snapshot` is called with `output_file` different from `input_file`
- **THEN** the result SHALL be written to `output_file` using atomic move

#### Scenario: output_file already exists
- **WHEN** `snapshot` is called with an `output_file` that already exists
- **THEN** the existing file SHALL be overwritten

### Requirement: Snapshot verifies manifest updates
`snapshot` SHALL correctly update the manifest with the new layer.

#### Scenario: New layer parent is previous default
- **WHEN** a snapshot is created
- **THEN** the new layer's `parent` SHALL be set to the previous default layer UUID

#### Scenario: Default is updated to new layer
- **WHEN** a snapshot is created
- **THEN** `manifest.default` SHALL be updated to the new layer UUID

### Requirement: Mount _resolve_target_layer handles UUID not in manifest
`_resolve_target_layer` SHALL try tag lookup when a valid UUID string is not found in the layers dict.

#### Scenario: Valid UUID format but not in layers
- **WHEN** `layer` is a valid UUID string that is not in the layers dict
- **THEN** tag lookup SHALL be attempted, and if not found, `MountError` SHALL be raised

### Requirement: PackError and UnpackError exception classes
`PackError` and `UnpackError` SHALL be properly defined exception classes that inherit from `Exception`.

#### Scenario: PackError message preservation
- **WHEN** `PackError("test message")` is created
- **THEN** `str(error)` SHALL contain "test message"

#### Scenario: UnpackError message preservation
- **WHEN** `UnpackError("test message")` is created
- **THEN** `str(error)` SHALL contain "test message"
