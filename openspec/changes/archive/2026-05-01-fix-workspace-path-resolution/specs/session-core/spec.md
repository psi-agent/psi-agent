## MODIFIED Requirements

### Requirement: Session calls system prompt builder

The session SHALL instantiate the `System` class from workspace systems and call its `build_system_prompt()` instance method. If systems/system.py does not exist or does not export a `System` class, no system prompt is included. The workspace path SHALL be resolved to an absolute path before being passed to the System class.

#### Scenario: System class instantiated on startup
- **WHEN** session starts and systems/system.py exists with `System` class
- **THEN** session instantiates `System(workspace_dir)` with the absolute workspace path
- **AND** the workspace_dir SHALL be a resolved absolute anyio.Path

#### Scenario: System prompt generated from instance method
- **WHEN** session processes a request and has a `System` instance
- **THEN** session calls `system.build_system_prompt()` and includes result in messages

#### Scenario: No system prompt when systems absent
- **WHEN** workspace does not have systems/system.py or no `System` class
- **THEN** messages do not include a system prompt

### Requirement: Session starts schedule executor on startup

The session SHALL start the schedule executor when session starts. The workspace path SHALL be resolved to an absolute path before loading schedules.

#### Scenario: Schedule executor initialized
- **WHEN** session starts with a workspace path
- **THEN** the schedule executor SHALL be initialized with the absolute workspace path
- **AND** schedules SHALL be loaded from the resolved absolute schedules/ directory

#### Scenario: Schedule executor runs in background
- **WHEN** session is running
- **THEN** all scheduled tasks SHALL run in background async tasks
- **AND** the session SHALL continue to handle HTTP requests

#### Scenario: No schedules directory
- **WHEN** workspace does not have a `schedules/` directory
- **THEN** session SHALL start normally without schedule executor

## ADDED Requirements

### Requirement: SessionRunner uses resolved workspace path

The SessionRunner SHALL obtain the workspace path by calling the async `workspace_path()` method and cache the resolved path.

#### Scenario: Workspace path resolved on runner initialization
- **WHEN** SessionRunner initializes via `__aenter__`
- **THEN** it SHALL call `await self.config.workspace_path()` to get the resolved absolute path
- **AND** store the resolved path for use by WorkspaceWatcher and System class

#### Scenario: WorkspaceWatcher receives absolute path
- **WHEN** WorkspaceWatcher is instantiated
- **THEN** it SHALL receive the resolved absolute workspace path
- **AND** correctly monitor files in the intended workspace location