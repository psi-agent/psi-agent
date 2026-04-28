## Why

The pyproject.toml is missing the project URL, which is a standard metadata field for Python packages. This is needed for PyPI package listing and provides users with a way to find the project repository and documentation.

## What Changes

- Add `project.urls` section to pyproject.toml with repository, homepage, and documentation links

## Capabilities

### New Capabilities

- `project-urls`: Adds standard project URL metadata (repository, homepage, documentation) to the package configuration

### Modified Capabilities

None - this is a new metadata addition with no existing capability changes.

## Impact

- pyproject.toml: Add `[project.urls]` section
- PyPI package page will display the project links
- No code changes required
