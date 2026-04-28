## ADDED Requirements

### Requirement: Manifest has valid structure
The manifest.json SHALL have a valid structure with required fields.

#### Scenario: Required fields present
- **WHEN** manifest.json is created or updated
- **THEN** it contains a `layers` object
- **AND** it contains a `default` field (single UUID string)
- **AND** `layers` contains at least one layer entry

### Requirement: Layer names are UUIDs
Each layer name in manifest.json SHALL be a valid UUID.

#### Scenario: UUID format layer names
- **WHEN** manifest is created
- **THEN** all layer names are UUID v4 format
- **AND** all layer names are unique

### Requirement: Manifest layer entries are valid
Each layer entry in manifest.json SHALL have valid structure.

#### Scenario: Root layer entry (no parent)
- **WHEN** manifest contains a root layer
- **THEN** the layer has no `parent` field
- **AND** the layer MAY have an optional `tag` field

#### Scenario: Non-root layer entry
- **WHEN** manifest contains a non-root layer
- **THEN** the layer has a `parent` field referencing an existing layer UUID
- **AND** the layer MAY have an optional `tag` field

### Requirement: Tags are unique and optional
Tags in manifest.json SHALL be unique across all layers and optional.

#### Scenario: Unique tags
- **WHEN** a layer has a tag
- **THEN** no other layer has the same tag
- **AND** the tag is a non-empty string

### Requirement: Manifest default field is valid
The default field SHALL reference an existing layer UUID.

#### Scenario: Default references existing layer
- **WHEN** manifest is valid
- **THEN** `default` is a single UUID string
- **AND** the UUID exists in `layers`

### Requirement: Manifest can be parsed
The system SHALL parse manifest.json correctly.

#### Scenario: Parse valid manifest
- **WHEN** system reads a valid manifest.json
- **THEN** system returns a Manifest data structure
- **AND** the data structure matches the JSON content

#### Scenario: Parse invalid manifest
- **WHEN** system reads an invalid manifest.json
- **THEN** system raises an exception with parse error details

### Requirement: Manifest can be serialized
The system SHALL serialize Manifest to JSON correctly.

#### Scenario: Serialize manifest
- **WHEN** system serializes a Manifest data structure
- **THEN** the output is valid JSON
- **AND** the JSON matches the manifest structure specification

### Requirement: Layer can be looked up by tag
The system SHALL support looking up layers by tag.

#### Scenario: Lookup by tag
- **WHEN** system receives a tag string
- **THEN** system returns the corresponding layer UUID
- **AND** system raises an exception if tag is not found

### Requirement: Layer chain can be resolved
The system SHALL resolve the complete layer chain from any layer.

#### Scenario: Resolve layer chain
- **WHEN** system receives a layer UUID or tag
- **THEN** system returns the complete chain from root to that layer
- **AND** the chain is ordered from root (first) to target layer (last)
