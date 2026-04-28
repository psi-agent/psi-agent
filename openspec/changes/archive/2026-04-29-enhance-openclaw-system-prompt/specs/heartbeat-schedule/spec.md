## ADDED Requirements

### Requirement: Heartbeat schedule task exists

The workspace SHALL include a heartbeat schedule task in `schedules/heartbeat/TASK.md` that runs every 30 minutes.

#### Scenario: Heartbeat task file exists
- **WHEN** the workspace is examined
- **THEN** a file exists at `schedules/heartbeat/TASK.md`

### Requirement: Heartbeat task reads HEARTBEAT.md

The heartbeat task SHALL instruct the agent to read HEARTBEAT.md and follow its instructions.

#### Scenario: Heartbeat task content
- **WHEN** the heartbeat task is executed
- **THEN** the agent reads HEARTBEAT.md from the workspace and executes any tasks specified within

### Requirement: Heartbeat task has correct cron schedule

The heartbeat task SHALL be configured with a cron schedule of every 30 minutes (`*/30 * * * *`).

#### Scenario: Heartbeat cron schedule
- **WHEN** the TASK.md is parsed
- **THEN** the cron field in the frontmatter is set to `*/30 * * * *`

### Requirement: Heartbeat task has descriptive name

The heartbeat task SHALL have a descriptive name and description in its frontmatter.

#### Scenario: Heartbeat task metadata
- **WHEN** the TASK.md is parsed
- **THEN** the name field describes the heartbeat functionality
- **AND** the description field explains what the task does
