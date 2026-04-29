## ADDED Requirements

### Requirement: Import placement at file header
All imports SHALL be placed at the file header, not inside function bodies.

#### Scenario: Imports at module level
- **WHEN** reading a Python file
- **THEN** all import statements SHALL appear at the top of the file, after the module docstring and `from __future__ import annotations`

### Requirement: Import order follows convention
Imports SHALL follow the order: stdlib → third-party → local, with each group separated by a blank line and sorted alphabetically within each group.

#### Scenario: Correct import order
- **WHEN** reading a Python file
- **THEN** imports SHALL appear in the order: standard library modules first, then third-party modules, then local project modules
