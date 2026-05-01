## Purpose

Ensure workspace paths are resolved to absolute paths at session initialization to guarantee consistent file access regardless of current working directory changes.

## ADDED Requirements

### Requirement: Workspace path resolution to absolute

The `SessionConfig.workspace_path()` method SHALL return an absolute path resolved from the workspace string.

#### Scenario: Relative workspace path resolved to absolute
- **WHEN** a relative workspace path like `./workspace` is provided to SessionConfig
- **THEN** `workspace_path()` SHALL return the absolute path equivalent
- **AND** the absolute path SHALL point to the same location as the relative path

#### Scenario: Absolute workspace path remains unchanged
- **WHEN** an absolute workspace path like `/home/user/workspace` is provided to SessionConfig
- **THEN** `workspace_path()` SHALL return the same absolute path

#### Scenario: Workspace path with symlinks resolved
- **WHEN** the workspace path contains symlinks
- **THEN** `workspace_path()` SHALL resolve to the canonical absolute path

### Requirement: Workspace path caching

The resolved workspace path SHALL be cached after first access to ensure consistency and efficiency.

#### Scenario: Subsequent calls return cached path
- **WHEN** `workspace_path()` is called multiple times
- **THEN** the same resolved absolute path object SHALL be returned
- **AND** path resolution SHALL only occur once

### Requirement: Async path resolution

The `workspace_path()` method SHALL be async to support async path resolution with anyio.

#### Scenario: Caller awaits workspace path
- **WHEN** code needs the workspace path
- **THEN** it SHALL call `await config.workspace_path()`
- **AND** the method SHALL return the resolved anyio.Path
