## ADDED Requirements

### Requirement: Session starts schedule executor on startup

The session SHALL start the schedule executor when session starts.

#### Scenario: Schedule executor initialized
- **WHEN** session starts with a workspace path
- **THEN** the schedule executor SHALL be initialized with the workspace schedules

#### Scenario: Schedule executor runs in background
- **WHEN** session is running
- **THEN** all scheduled tasks SHALL run in background async tasks
- **AND** the session SHALL continue to handle HTTP requests

#### Scenario: No schedules directory
- **WHEN** workspace does not have a `schedules/` directory
- **THEN** session SHALL start normally without schedule executor
