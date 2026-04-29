## ADDED Requirements

### Requirement: Cache directory uses platform-specific location
The system SHALL use `platformdirs.user_cache_dir()` to determine the default cache directory location, ensuring compliance with platform-specific conventions.

#### Scenario: Linux cache directory
- **WHEN** the system runs on Linux
- **THEN** the cache directory SHALL be located at `~/.cache/psi-agent/` following XDG Base Directory Specification

#### Scenario: macOS cache directory
- **WHEN** the system runs on macOS
- **THEN** the cache directory SHALL be located at `~/Library/Caches/psi-agent/` following Apple guidelines

#### Scenario: Windows cache directory
- **WHEN** the system runs on Windows
- **THEN** the cache directory SHALL be located at `%LOCALAPPDATA%\psi-agent\` following Microsoft guidelines

### Requirement: No pathlib.Path imports in source code
The source code SHALL NOT import `pathlib.Path` directly, using `anyio.Path` for all path operations and `platformdirs` for determining platform-specific directories.

#### Scenario: Source code review
- **WHEN** reviewing source files in `src/`
- **THEN** no file SHALL contain `from pathlib import Path` or `import pathlib`
