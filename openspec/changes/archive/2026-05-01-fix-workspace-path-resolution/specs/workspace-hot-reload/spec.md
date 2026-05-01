## MODIFIED Requirements

### Requirement: Tool Change Detection

The system SHALL detect changes to tool files on every user message. Tool files SHALL be looked up in the absolute workspace path.

Tool files are Python files (`.py`) in the `tools/` directory. Changes include:
- Modified files (hash changed)
- New files added
- Files removed

#### Scenario: Tool file modified
- **WHEN** a tool file's content changes (hash differs from cached value)
- **THEN** the system SHALL reload that tool and update the tool registry
- **AND** the system SHALL log the update at INFO level

#### Scenario: New tool file added
- **WHEN** a new `.py` file appears in the `tools/` directory
- **THEN** the system SHALL load the new tool and register it
- **AND** the system SHALL log the addition at INFO level

#### Scenario: Tool file removed
- **WHEN** a `.py` file is removed from the `tools/` directory
- **THEN** the system SHALL unregister that tool
- **AND** the system SHALL log the removal at INFO level

### Requirement: Skill Change Detection

The system SHALL detect changes to skill files on every user message. Skill files SHALL be looked up in the absolute workspace path.

Skill files are `SKILL.md` files in `skills/*/` subdirectories. Changes include:
- Modified files (hash changed)
- New skill directories with SKILL.md
- Skill directories removed

#### Scenario: Skill file modified
- **WHEN** a `SKILL.md` file's content changes (hash differs from cached value)
- **THEN** the system SHALL mark the system prompt cache as stale
- **AND** the system SHALL log the update at INFO level

#### Scenario: New skill added
- **WHEN** a new subdirectory with `SKILL.md` appears in the `skills/` directory
- **THEN** the system SHALL mark the system prompt cache as stale
- **AND** the system SHALL log the addition at INFO level

#### Scenario: Skill removed
- **WHEN** a skill subdirectory is removed from the `skills/` directory
- **THEN** the system SHALL mark the system prompt cache as stale
- **AND** the system SHALL log the removal at INFO level

### Requirement: Schedule Change Detection

The system SHALL detect changes to schedule files on every user message. Schedule files SHALL be looked up in the absolute workspace path.

Schedule files are `TASK.md` files in `schedules/*/` subdirectories. Changes include:
- Modified files (hash changed)
- New schedule directories with TASK.md
- Schedule directories removed

#### Scenario: Schedule file modified
- **WHEN** a `TASK.md` file's content changes (hash differs from cached value)
- **THEN** the system SHALL reload that schedule
- **AND** the system SHALL update the schedule executor
- **AND** the system SHALL log the update at INFO level

#### Scenario: New schedule added
- **WHEN** a new subdirectory with `TASK.md` appears in the `schedules/` directory
- **THEN** the system SHALL load the new schedule
- **AND** the system SHALL add it to the schedule executor
- **AND** the system SHALL log the addition at INFO level

#### Scenario: Schedule removed
- **WHEN** a schedule subdirectory is removed from the `schedules/` directory
- **THEN** the system SHALL remove that schedule from the executor
- **AND** the system SHALL log the removal at INFO level

## ADDED Requirements

### Requirement: WorkspaceWatcher uses absolute workspace path

The WorkspaceWatcher SHALL be initialized with and use the resolved absolute workspace path for all file monitoring operations.

#### Scenario: WorkspaceWatcher initialized with absolute path
- **WHEN** WorkspaceWatcher is created
- **THEN** it SHALL receive the resolved absolute workspace path
- **AND** all subdirectory paths (tools/, skills/, schedules/) SHALL be derived from this absolute path

#### Scenario: File scanning uses absolute paths
- **WHEN** scanning for tools, skills, or schedules
- **THEN** the system SHALL use the absolute workspace path to construct subdirectory paths
- **AND** file detection SHALL work correctly regardless of the current working directory