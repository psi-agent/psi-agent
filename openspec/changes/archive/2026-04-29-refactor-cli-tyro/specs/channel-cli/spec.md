## MODIFIED Requirements

### Requirement: CLI accepts session socket and message

The CLI SHALL accept session socket path and user message as command line arguments.

#### Scenario: CLI with required arguments
- **WHEN** user runs `psi-agent channel cli --session-socket ./session.sock --message "Hello"`
- **THEN** the CLI connects to the session socket and sends the message
