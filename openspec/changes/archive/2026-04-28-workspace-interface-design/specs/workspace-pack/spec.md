## ADDED Requirements

### Requirement: Pack creates squashfs from directory
The system SHALL create a squashfs image from a workspace directory.

#### Scenario: Pack workspace directory
- **WHEN** user runs `psi-workspace-pack --input ./workspace --output ./workspace.squashfs`
- **THEN** system creates a squashfs image at the specified output path
- **AND** the squashfs contains the input directory contents in a UUID-named folder
- **AND** the squashfs contains a `manifest.json` with the layer defined

#### Scenario: Pack with tag
- **WHEN** user runs `psi-workspace-pack --input ./workspace --output ./workspace.squashfs --tag v1.0`
- **THEN** system creates a squashfs with the layer tagged as "v1.0"
- **AND** manifest.json contains the tag for that layer

### Requirement: Pack creates valid manifest
The system SHALL create a valid manifest.json in the squashfs.

#### Scenario: Manifest structure
- **WHEN** pack completes successfully
- **THEN** manifest.json contains a `layers` object with one UUID key
- **AND** manifest.json contains a `default` field with the UUID
- **AND** the layer has no `parent` field (root layer)

### Requirement: Pack generates UUID for layer
The system SHALL generate a UUID for the layer name.

#### Scenario: UUID generation
- **WHEN** pack creates a new squashfs
- **THEN** the layer name is a valid UUID v4
- **AND** the directory name in squashfs matches the UUID

### Requirement: Pack validates input directory
The system SHALL validate the input directory exists and is readable.

#### Scenario: Invalid input directory
- **WHEN** user specifies a non-existent input directory
- **THEN** system raises an exception with a clear error message
- **AND** no output file is created

### Requirement: Pack uses async IO
The system SHALL use async operations for all file system operations.

#### Scenario: Async file operations
- **WHEN** pack is running
- **THEN** all file reads and writes use async methods
- **AND** the squashfs creation does not block the event loop
