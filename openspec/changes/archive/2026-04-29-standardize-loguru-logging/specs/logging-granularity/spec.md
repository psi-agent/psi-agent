## ADDED Requirements

### Requirement: DEBUG-level logging for inter-component communication

All components SHALL log inter-component communication inputs and outputs at DEBUG level.

#### Scenario: HTTP request logging
- **WHEN** a component sends an HTTP request to another component
- **THEN** the request body SHALL be logged at DEBUG level as formatted JSON

#### Scenario: HTTP response logging
- **WHEN** a component receives an HTTP response from another component
- **THEN** the response body SHALL be logged at DEBUG level as formatted JSON

#### Scenario: Sensitive data masking in DEBUG logs
- **WHEN** logging request/response bodies that contain sensitive data (API keys, tokens, passwords)
- **THEN** the sensitive values SHALL be masked with `***`

### Requirement: DEBUG-level logging for tool execution

The session component SHALL log tool execution details at DEBUG level.

#### Scenario: Tool execution input logging
- **WHEN** a tool is executed
- **THEN** the tool name and arguments SHALL be logged at DEBUG level

#### Scenario: Tool execution result logging
- **WHEN** a tool execution completes
- **THEN** the result SHALL be logged at DEBUG level (truncated if longer than 500 characters)

### Requirement: DEBUG-level logging for schedule execution

The session component SHALL log schedule execution details at DEBUG level.

#### Scenario: Schedule execution logging
- **WHEN** a scheduled task is executed
- **THEN** the schedule name and content SHALL be logged at DEBUG level

#### Scenario: Schedule timing logging
- **WHEN** a schedule loop calculates next run time
- **THEN** the next run time SHALL be logged at DEBUG level

### Requirement: DEBUG-level logging for workspace changes

The workspace watcher SHALL log detected changes at DEBUG level.

#### Scenario: Workspace change detection logging
- **WHEN** workspace changes are detected
- **THEN** the change summary (added/removed/modified items) SHALL be logged at DEBUG level

### Requirement: DEBUG-level logging for command execution

Workspace components SHALL log command execution details at DEBUG level.

#### Scenario: Command execution logging
- **WHEN** a shell command is executed (mount, umount, mksquashfs, unsquashfs)
- **THEN** the full command SHALL be logged at DEBUG level

#### Scenario: Command output logging
- **WHEN** a shell command completes
- **THEN** the command output (stdout/stderr) SHALL be logged at DEBUG level

### Requirement: INFO-level logging for lifecycle events

All components SHALL log significant lifecycle events at INFO level.

#### Scenario: Component startup logging
- **WHEN** a component starts
- **THEN** the component name and key configuration (excluding sensitive data) SHALL be logged at INFO level

#### Scenario: Component shutdown logging
- **WHEN** a component stops
- **THEN** the component name SHALL be logged at INFO level

### Requirement: INFO-level logging for request handling

Server components SHALL log request handling at INFO level.

#### Scenario: Request received logging
- **WHEN** a server receives a request
- **THEN** the request method and path SHALL be logged at INFO level

#### Scenario: Response sent logging
- **WHEN** a server sends a response
- **THEN** the response status (success/error) SHALL be logged at INFO level

### Requirement: INFO-level logging for tool management

The session component SHALL log tool management events at INFO level.

#### Scenario: Tool loaded logging
- **WHEN** a tool is loaded
- **THEN** the tool name SHALL be logged at INFO level

#### Scenario: Tool updated logging
- **WHEN** a tool is updated via hot-reload
- **THEN** the tool name SHALL be logged at INFO level with "Updated" prefix

#### Scenario: Tool removed logging
- **WHEN** a tool is removed via hot-reload
- **THEN** the tool name SHALL be logged at INFO level with "Removed" prefix

### Requirement: INFO-level logging for schedule management

The session component SHALL log schedule management events at INFO level.

#### Scenario: Schedule started logging
- **WHEN** a schedule loop starts
- **THEN** the schedule name SHALL be logged at INFO level

#### Scenario: Schedule completed logging
- **WHEN** a scheduled task completes
- **THEN** the schedule name SHALL be logged at INFO level

### Requirement: INFO-level logging for workspace operations

Workspace components SHALL log workspace operations at INFO level.

#### Scenario: Pack operation logging
- **WHEN** a workspace is packed
- **THEN** the input and output paths SHALL be logged at INFO level

#### Scenario: Mount operation logging
- **WHEN** a workspace is mounted
- **THEN** the squashfs path and mount point SHALL be logged at INFO level

#### Scenario: Unmount operation logging
- **WHEN** a workspace is unmounted
- **THEN** the mount point SHALL be logged at INFO level

#### Scenario: Snapshot operation logging
- **WHEN** a snapshot is created
- **THEN** the mount point and output path SHALL be logged at INFO level

#### Scenario: Unpack operation logging
- **WHEN** a squashfs is unpacked
- **THEN** the input and output paths SHALL be logged at INFO level
