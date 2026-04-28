## ADDED Requirements

### Requirement: Unpack extracts squashfs to directory
The system SHALL extract a squashfs image to a directory without mounting.

#### Scenario: Unpack squashfs
- **WHEN** user runs `psi-workspace-unpack --input ./workspace.squashfs --output ./workspace`
- **THEN** system extracts the squashfs contents to the output directory
- **AND** the output directory structure matches the squashfs internal structure
- **AND** overlay layers are created as separate directories

### Requirement: Unpack preserves overlay structure
The system SHALL create directories matching the squashfs overlay structure.

#### Scenario: Multiple layers unpacked
- **WHEN** squashfs contains base/, layer-1/, layer-2/ and manifest.json
- **THEN** output directory contains base/, layer-1/, layer-2/ directories
- **AND** manifest.json is copied to output directory

### Requirement: Unpack validates input file
The system SHALL validate the input squashfs exists and is readable.

#### Scenario: Invalid input file
- **WHEN** user specifies a non-existent squashfs file
- **THEN** system raises an exception with a clear error message
- **AND** no output directory is created

### Requirement: Unpack uses async IO
The system SHALL use async operations for all file system operations.

#### Scenario: Async extraction
- **WHEN** unpack is running
- **THEN** all file reads and writes use async methods
