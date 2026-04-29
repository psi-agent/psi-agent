## MODIFIED Requirements

### Requirement: Alpha tag triggers PyPI publish
The `auto-alpha-tag.yml` workflow SHALL include a `publish` job that publishes the package to PyPI when a new alpha tag is successfully created.

#### Scenario: New alpha tag triggers publish
- **WHEN** the `auto-tag` job successfully creates and pushes a new alpha tag
- **THEN** the `publish` job SHALL run and publish the package to PyPI

#### Scenario: No new tag skips publish
- **WHEN** the `auto-tag` job does not create a new tag (already exists, no CI runs, etc.)
- **THEN** the `publish` job SHALL be skipped

#### Scenario: Output naming consistency
- **WHEN** the `create-tag` step sets outputs
- **THEN** the outputs SHALL use consistent naming: `tag-created` and `tag-name`
