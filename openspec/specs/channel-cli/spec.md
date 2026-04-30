## ADDED Requirements

### Requirement: CLI accepts session socket and message

The CLI SHALL accept session socket path and user message as command line arguments.

#### Scenario: CLI with required arguments
- **WHEN** user runs `psi-agent channel cli --session-socket ./session.sock --message "Hello"` or `psi-channel-cli --session-socket ./session.sock --message "Hello"`
- **THEN** the CLI connects to the session socket and sends the message

### Requirement: CLI sends request to session

The CLI SHALL send an OpenAI chat completion request to the session.

#### Scenario: Request sent to session
- **WHEN** CLI connects to session socket
- **THEN** a POST /v1/chat/completions request is sent with the user message

### Requirement: CLI outputs response to stdout

The CLI SHALL output the agent response to stdout.

#### Scenario: Non-streaming response output
- **WHEN** session returns a non-streaming response
- **THEN** the response content is printed to stdout

#### Scenario: Streaming response output
- **WHEN** session returns a streaming response with `--stream` flag (default)
- **THEN** each chunk is printed to stdout as it arrives

#### Scenario: Disable streaming with flag
- **WHEN** CLI is invoked with `--no-stream` flag
- **THEN** streaming mode SHALL be disabled
- **AND** the CLI SHALL wait for complete response before output

### Requirement: CLI exits after response

The CLI SHALL exit after receiving and outputting the response.

#### Scenario: CLI exits after response
- **WHEN** response is fully received and output
- **THEN** the CLI process exits with code 0

### Requirement: CLI handles connection errors

The CLI SHALL handle connection errors gracefully.

#### Scenario: Session socket not found
- **WHEN** session socket path does not exist
- **THEN** an error message is printed to stderr and CLI exits with non-zero code