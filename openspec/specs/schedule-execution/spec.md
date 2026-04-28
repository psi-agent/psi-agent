## ADDED Requirements

### Requirement: Schedule loader scans workspace schedules directory

The session SHALL load schedule tasks from the workspace `schedules/` directory on startup.

#### Scenario: Load schedules on startup
- **WHEN** session starts with a workspace path
- **THEN** the session SHALL scan `<workspace>/schedules/` for subdirectories
- **AND** each subdirectory containing `TASK.md` SHALL be loaded as a schedule

#### Scenario: Parse TASK.md with YAML frontmatter
- **WHEN** a `TASK.md` file is found
- **THEN** the session SHALL parse YAML frontmatter to extract `name`, `description`, and `cron` fields
- **AND** the task content (after frontmatter) SHALL be stored as the task instruction

#### Scenario: Handle missing cron field
- **WHEN** a `TASK.md` file has no `cron` field in frontmatter
- **THEN** the session SHALL log a warning and skip that schedule

### Requirement: Schedule executor runs tasks at cron intervals

The session SHALL execute schedule tasks according to their cron expressions.

#### Scenario: Execute task at scheduled time
- **WHEN** the current time matches the cron expression
- **THEN** the session SHALL execute the task

#### Scenario: Send task content as user message
- **WHEN** a scheduled task is executed
- **THEN** the TASK.md content SHALL be sent to the LLM as a user message

#### Scenario: Calculate next run time
- **WHEN** a task is scheduled
- **THEN** the session SHALL calculate the next run time using the cron expression
- **AND** the session SHALL wait until that time before executing

### Requirement: Schedule uses standard 5-field cron format

The session SHALL support standard 5-field cron expressions.

#### Scenario: Parse valid cron expression
- **WHEN** a cron expression like `"0 9 * * *"` (9am daily) is provided
- **THEN** the session SHALL correctly parse and interpret it

#### Scenario: Support all cron fields
- **WHEN** parsing cron expressions
- **THEN** the session SHALL support minute, hour, day of month, month, day of week fields

### Requirement: Multiple schedules run concurrently

The session SHALL support running multiple scheduled tasks concurrently.

#### Scenario: Multiple schedules
- **WHEN** multiple schedules are defined in the workspace
- **THEN** each schedule SHALL run independently in its own async task

#### Scenario: Independent execution
- **WHEN** one schedule is executing
- **THEN** other schedules SHALL NOT be blocked

### Requirement: Schedule execution uses async architecture

All schedule operations SHALL use async/await for I/O operations.

#### Scenario: Async file loading
- **WHEN** loading TASK.md files
- **THEN** the session SHALL use `anyio.open_file()` for async file reading

#### Scenario: Async sleep for scheduling
- **WHEN** waiting for next scheduled time
- **THEN** the session SHALL use `asyncio.sleep()` to avoid blocking