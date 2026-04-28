## ADDED Requirements

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

### Requirement: DEBUG-level logging for tool execution

The session component SHALL log tool execution details at DEBUG level:
- Tool name
- Tool arguments (full content)
- Tool result (full content, truncated if excessively long)

#### Scenario: Tool execution logging
- **WHEN** psi-session executes a tool
- **THEN** the tool name, arguments, and result SHALL be logged at DEBUG level

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

### Requirement: DEBUG-level logging for workspace operations

All workspace components SHALL log file I/O operations at DEBUG level:
- File paths being read/written
- Command execution (mksquashfs, unsquashfs, mount, umount)
- Command output (stdout/stderr)

#### Scenario: Squashfs command logging
- **WHEN** psi-workspace-pack creates a squashfs image
- **THEN** the mksquashfs command and output SHALL be logged at DEBUG level

#### Scenario: Mount command logging
- **WHEN** psi-workspace-mount mounts a squashfs image
- **THEN** the mount command and output SHALL be logged at DEBUG level

### Requirement: INFO-level logging consistency

All components SHALL log the following at INFO level:
- Component startup with key configuration (excluding sensitive values)
- Component shutdown
- Request received (without body details)
- Response sent (without body details)
- Tool/schedule execution started/completed (name only)
- Errors with sufficient context

#### Scenario: Component startup logging
- **WHEN** any psi-agent component starts
- **THEN** the component name and key configuration SHALL be logged at INFO level

#### Scenario: Component shutdown logging
- **WHEN** any psi-agent component stops
- **THEN** a shutdown message SHALL be logged at INFO level

#### Scenario: Request received logging
- **WHEN** a server component receives a request
- **THEN** the request method and path SHALL be logged at INFO level (without body)

#### Scenario: Tool execution summary logging
- **WHEN** a tool execution completes
- **THEN** the tool name and success/failure status SHALL be logged at INFO level

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
