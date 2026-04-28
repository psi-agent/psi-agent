## Logging Standards

This specification defines logging requirements for all psi-agent components.

### Requirement: Use loguru for all logging

All psi-agent components SHALL use loguru for logging.

#### Scenario: Import loguru
- **WHEN** a component needs to log
- **THEN** it SHALL import and use `from loguru import logger`

### Requirement: DEBUG-level logging for HTTP communications

All HTTP client and server components SHALL log the following at DEBUG level:
- Request URL and method
- Request headers (with sensitive values masked)
- Request body (full content, with sensitive values masked)
- Response status code
- Response body (full content, truncated if excessively long)

#### Scenario: HTTP request logging in psi-ai client
- **WHEN** psi-ai-openai-completions or psi-ai-anthropic-messages sends a request to an LLM API
- **THEN** the request URL, headers (with API key masked), and body SHALL be logged at DEBUG level

#### Scenario: HTTP response logging in psi-ai client
- **WHEN** psi-ai-openai-completions or psi-ai-anthropic-messages receives a response from an LLM API
- **THEN** the response status code and body SHALL be logged at DEBUG level

#### Scenario: HTTP request logging in psi-session server
- **WHEN** psi-session receives an HTTP request from a channel
- **THEN** the request method, path, and body SHALL be logged at DEBUG level

#### Scenario: HTTP response logging in psi-session server
- **WHEN** psi-session sends an HTTP response to a channel
- **THEN** the response status and body SHALL be logged at DEBUG level

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

The session component SHALL log tool execution details at DEBUG level:
- Tool name
- Tool arguments (full content)
- Tool result (full content, truncated if excessively long)

#### Scenario: Tool execution input logging
- **WHEN** a tool is executed
- **THEN** the tool name and arguments SHALL be logged at DEBUG level

#### Scenario: Tool execution result logging
- **WHEN** a tool execution completes
- **THEN** the result SHALL be logged at DEBUG level (truncated if longer than 500 characters)

#### Scenario: Tool execution error logging
- **WHEN** a tool execution fails
- **THEN** the error details SHALL be logged at ERROR level with full context

### Requirement: DEBUG-level logging for schedule execution

The session component SHALL log schedule execution details at DEBUG level:
- Schedule name
- Schedule content (the task instruction)
- Execution result

#### Scenario: Schedule execution logging
- **WHEN** psi-session executes a scheduled task
- **THEN** the schedule name and content SHALL be logged at DEBUG level before execution

#### Scenario: Schedule execution result logging
- **WHEN** a scheduled task completes
- **THEN** the result SHALL be logged at DEBUG level

#### Scenario: Schedule timing logging
- **WHEN** a schedule loop calculates next run time
- **THEN** the next run time SHALL be logged at DEBUG level

### Requirement: DEBUG-level logging for workspace operations

All workspace components SHALL log file I/O operations at DEBUG level:
- File paths being read/written
- Command execution (mksquashfs, unsquashfs, mount, umount)
- Command output (stdout/stderr)

#### Scenario: Workspace change detection logging
- **WHEN** workspace changes are detected
- **THEN** the change summary (added/removed/modified items) SHALL be logged at DEBUG level

#### Scenario: Squashfs command logging
- **WHEN** psi-workspace-pack creates a squashfs image
- **THEN** the mksquashfs command and output SHALL be logged at DEBUG level

#### Scenario: Mount command logging
- **WHEN** psi-workspace-mount mounts a squashfs image
- **THEN** the mount command and output SHALL be logged at DEBUG level

#### Scenario: Command execution logging
- **WHEN** a shell command is executed (mount, umount, mksquashfs, unsquashfs)
- **THEN** the full command SHALL be logged at DEBUG level

#### Scenario: Command output logging
- **WHEN** a shell command completes
- **THEN** the command output (stdout/stderr) SHALL be logged at DEBUG level

### Requirement: INFO-level logging for lifecycle events

All components SHALL log significant lifecycle events at INFO level:
- Component startup with key configuration (excluding sensitive values)
- Component shutdown

#### Scenario: Component startup logging
- **WHEN** any psi-agent component starts
- **THEN** the component name and key configuration SHALL be logged at INFO level

#### Scenario: Component shutdown logging
- **WHEN** any psi-agent component stops
- **THEN** a shutdown message SHALL be logged at INFO level

### Requirement: INFO-level logging for request handling

Server components SHALL log request handling at INFO level:
- Request received (without body details)
- Response sent (without body details)

#### Scenario: Request received logging
- **WHEN** a server receives a request
- **THEN** the request method and path SHALL be logged at INFO level (without body)

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

#### Scenario: Tool execution summary logging
- **WHEN** a tool execution completes
- **THEN** the tool name and success/failure status SHALL be logged at INFO level

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

### Requirement: Sensitive data masking

All components SHALL mask sensitive values in logs:
- API keys SHALL be replaced with `***` or `*** (hidden)`
- Tokens SHALL be replaced with `***`
- Passwords SHALL be replaced with `***`

#### Scenario: API key masking in request logs
- **WHEN** logging an HTTP request with an Authorization header
- **THEN** the header value SHALL be logged as `Bearer *** (hidden)` or similar

#### Scenario: API key masking in config logs
- **WHEN** logging configuration that includes an API key
- **THEN** the API key SHALL NOT be included in the log output

### Requirement: ERROR-level logging for failures

All components SHALL log errors with sufficient context at ERROR level.

#### Scenario: Error logging with context
- **WHEN** an error occurs
- **THEN** the error message and relevant context SHALL be logged at ERROR level