## ADDED Requirements

### Requirement: Project URLs metadata

The pyproject.toml SHALL include a `[project.urls]` section with standard project links.

#### Scenario: PyPI displays project links

- **WHEN** the package is published to PyPI
- **THEN** the package page displays links to repository, homepage, and documentation

#### Scenario: Build tools parse URLs

- **WHEN** build tools parse pyproject.toml
- **THEN** they can extract the project URLs from the `[project.urls]` section
