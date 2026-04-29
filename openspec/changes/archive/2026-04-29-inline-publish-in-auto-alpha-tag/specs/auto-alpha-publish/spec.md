## ADDED Requirements

### Requirement: Alpha tag triggers PyPI publish
The `auto-alpha-tag.yml` workflow SHALL include a `publish` job that publishes the package to PyPI when a new alpha tag is successfully created.

#### Scenario: New alpha tag triggers publish
- **WHEN** the `auto-tag` job successfully creates and pushes a new alpha tag
- **THEN** the `publish` job SHALL run and publish the package to PyPI

#### Scenario: No new tag skips publish
- **WHEN** the `auto-tag` job does not create a new tag (already exists, no CI runs, etc.)
- **THEN** the `publish` job SHALL be skipped

### Requirement: Publish job uses trusted publishing
The `publish` job in `auto-alpha-tag.yml` SHALL use the same trusted publishing mechanism as `ci.yml` (OIDC token with PyPI).

#### Scenario: Trusted publishing configuration
- **WHEN** the `publish` job runs
- **THEN** it SHALL use `uv publish` with OIDC authentication via the `pypi` environment

### Requirement: Publish job depends on auto-tag
The `publish` job SHALL have `needs: [auto-tag]` dependency to ensure it only runs after tag creation.

#### Scenario: Job ordering
- **WHEN** the workflow runs
- **THEN** the `publish` job SHALL wait for the `auto-tag` job to complete before starting
