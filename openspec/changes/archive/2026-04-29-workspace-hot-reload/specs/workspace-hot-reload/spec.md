## ADDED Requirements

### Requirement: Tool Change Detection

The system SHALL detect changes to tool files on every user message.

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

The system SHALL detect changes to skill files on every user message.

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

The system SHALL detect changes to schedule files on every user message.

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

### Requirement: System Prompt Rebuild

The system SHALL rebuild the system prompt when skills or schedules change.

#### Scenario: Skills changed triggers system prompt rebuild

- **WHEN** any skill is added, modified, or removed
- **THEN** the system SHALL call `build_system_prompt()` to rebuild the system prompt
- **AND** the system SHALL update the cached system prompt

#### Scenario: Tools changed does not trigger system prompt rebuild

- **WHEN** any tool is added, modified, or removed
- **THEN** the system SHALL NOT rebuild the system prompt
- **AND** the system SHALL only update the tool registry

### Requirement: Change Detection Timing

The system SHALL perform change detection before processing each user message.

#### Scenario: Change detection before message processing

- **WHEN** a user message is received
- **THEN** the system SHALL first check for workspace file changes
- **AND** the system SHALL apply any detected changes
- **AND** only then SHALL the system process the user message

### Requirement: Hash-Based Change Detection

The system SHALL use MD5 file hashes to detect file modifications.

#### Scenario: Hash comparison for modification detection

- **WHEN** checking if a file has changed
- **THEN** the system SHALL compute the MD5 hash of the file content
- **AND** the system SHALL compare it to the cached hash
- **AND** if hashes differ, the file SHALL be considered modified
