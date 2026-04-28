## Context

The pyproject.toml file currently defines project metadata (name, description, authors, etc.) but is missing the `[project.urls]` section. This is a standard PEP 621 metadata field that provides links to the project's repository, homepage, and documentation.

## Goals / Non-Goals

**Goals:**
- Add standard project URL metadata to pyproject.toml
- Ensure PyPI displays proper links when the package is published

**Non-Goals:**
- Modifying any code or functionality
- Changing existing metadata fields

## Decisions

### URL Structure

Add the following URLs to `[project.urls]`:
- `Repository`: https://github.com/psi-agent/psi-agent
- `Homepage`: Same as repository (project is hosted on GitHub)
- `Documentation`: README file served as documentation

This follows the standard pattern for Python packages hosted on GitHub.

## Risks / Trade-offs

No significant risks. This is a metadata-only change with no impact on functionality.
