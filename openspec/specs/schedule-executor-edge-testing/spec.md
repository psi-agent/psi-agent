## ADDED Requirements

### Requirement: ScheduleExecutor _schedule_loop handles exceptions and retries
`ScheduleExecutor._schedule_loop` SHALL handle exceptions during task execution by sleeping 60 seconds and retrying.

#### Scenario: Exception during task execution triggers retry
- **WHEN** `_execute_task` raises an exception
- **THEN** the loop SHALL log the error, sleep 60 seconds, and continue

#### Scenario: CancelledError stops the loop
- **WHEN** `asyncio.CancelledError` is raised during the loop
- **THEN** the loop SHALL exit cleanly

#### Scenario: Immediate execution when next run is due
- **WHEN** `get_seconds_until_next_run` returns 0
- **THEN** the task SHALL execute immediately without sleeping

### Requirement: ScheduleExecutor handles duplicate and concurrent operations
`ScheduleExecutor` SHALL handle edge cases in add/remove/update operations.

#### Scenario: Add schedule with duplicate name
- **WHEN** `add_schedule` is called with a schedule name that already exists
- **THEN** both schedules SHALL exist in the list (no deduplication required)

#### Scenario: Add schedule when executor not running
- **WHEN** `add_schedule` is called when the executor is not started
- **THEN** the schedule SHALL be added to the list but no task SHALL be created

#### Scenario: Remove schedule that is currently executing
- **WHEN** `remove_schedule` is called for a schedule that is mid-execution
- **THEN** the schedule SHALL be removed from the list and its task SHALL be cancelled

#### Scenario: Update schedule that is currently executing
- **WHEN** `update_schedule` is called for a schedule that is mid-execution
- **THEN** the schedule SHALL be replaced and its task SHALL be cancelled and restarted

### Requirement: ScheduleExecutor handles double start/stop
`ScheduleExecutor` SHALL handle being started or stopped multiple times.

#### Scenario: Double start
- **WHEN** `start()` is called twice without `stop()` in between
- **THEN** the executor SHALL handle this gracefully (no duplicate tasks)

#### Scenario: Double stop
- **WHEN** `stop()` is called twice
- **THEN** no exception SHALL be raised on the second call

### Requirement: Schedule handles invalid cron expressions
`Schedule.get_next_run` SHALL handle invalid cron expressions.

#### Scenario: Invalid cron expression
- **WHEN** a Schedule is created with an invalid cron expression
- **THEN** `get_next_run` SHALL raise an appropriate exception (from croniter)

### Requirement: parse_frontmatter handles YAML edge cases
`parse_frontmatter` SHALL handle various YAML formatting edge cases.

#### Scenario: Frontmatter with blank lines between key-value pairs
- **WHEN** frontmatter has blank lines between key-value pairs
- **THEN** parsing SHALL succeed and extract all key-value pairs

#### Scenario: Frontmatter value containing hash character
- **WHEN** a frontmatter value contains `#` (potential YAML comment)
- **THEN** the `#` SHALL be preserved in the value if properly quoted
