## ADDED Requirements

### Requirement: parse_manifest validates layer data types
`parse_manifest` SHALL raise `ManifestParseError` when layer data is not a dict, has invalid parent UUID format, or has non-string tag.

#### Scenario: Layer data is not a dict
- **WHEN** a layer value is a string or number instead of a dict
- **THEN** `ManifestParseError` SHALL be raised with message containing "must be an object"

#### Scenario: Invalid parent UUID format
- **WHEN** a layer has a `parent` field that is not a valid UUID string
- **THEN** `ManifestParseError` SHALL be raised with message about invalid parent UUID

#### Scenario: Tag is not a string
- **WHEN** a layer has a `tag` field that is a number instead of a string
- **THEN** `ManifestParseError` SHALL be raised with message about tag type

#### Scenario: Default is invalid UUID format
- **WHEN** the `default` field is not a valid UUID string
- **THEN** `ManifestParseError` SHALL be raised with message about invalid default UUID

#### Scenario: Layer with empty dict
- **WHEN** a layer is an empty dict `{}`
- **THEN** parsing SHALL succeed with `parent=None` and `tag=None`

#### Scenario: Tag is explicitly null
- **WHEN** a layer has `"tag": null`
- **THEN** parsing SHALL succeed with `tag=None`

### Requirement: Manifest resolve_chain handles broken chains
`Manifest.resolve_chain` SHALL raise `ValueError` when a layer's parent references a UUID not in the layers dict.

#### Scenario: Broken chain with missing grandparent
- **WHEN** layer C has parent B, layer B has parent A, but A is not in the layers dict
- **THEN** `ValueError` SHALL be raised

### Requirement: Manifest get_children handles missing UUID
`Manifest.get_children` SHALL return an empty list when the parent UUID is not in the layers dict.

#### Scenario: UUID not in layers
- **WHEN** `get_children` is called with a UUID not in the layers dict
- **THEN** an empty list SHALL be returned

### Requirement: Manifest get_root_layers handles multiple roots
`Manifest.get_root_layers` SHALL correctly identify all root layers in a manifest with disconnected layer graphs.

#### Scenario: Multiple root layers
- **WHEN** the manifest has two layers with no parent (disconnected graph)
- **THEN** both SHALL be returned as root layers

### Requirement: Manifest lookup_by_tag handles special characters
`Manifest.lookup_by_tag` SHALL handle tags with special characters.

#### Scenario: Tag with empty string
- **WHEN** `lookup_by_tag` is called with an empty string
- **THEN** `ManifestParseError` SHALL be raised (tag not found)

### Requirement: serialize_manifest handles default=None
`serialize_manifest` SHALL handle the case where `manifest.default` is `None` in a way that is consistent with `parse_manifest`.

#### Scenario: Serialize manifest with default=None
- **WHEN** a manifest has `default=None`
- **THEN** the serialized output SHALL either be re-parseable or this SHALL be documented as an invalid state

### Requirement: ManifestParseError preserves details
`ManifestParseError` SHALL correctly format the error message when `details` is provided.

#### Scenario: ManifestParseError with details
- **WHEN** `ManifestParseError("msg", details="detail")` is created
- **THEN** `str(error)` SHALL contain both "msg" and "detail"
