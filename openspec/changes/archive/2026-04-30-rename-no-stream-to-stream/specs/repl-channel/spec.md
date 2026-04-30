## MODIFIED Requirements

### Requirement: REPL uses streaming by default

The REPL SHALL use streaming requests by default for better user experience.

#### Scenario: Default streaming request
- **WHEN** user enters a message
- **THEN** REPL SHALL send request with `stream: true`
- **AND** display response chunks in real-time

#### Scenario: Real-time output display
- **WHEN** streaming response arrives
- **THEN** REPL SHALL print each content chunk immediately
- **AND** NOT wait for complete response

#### Scenario: Disable streaming with flag
- **WHEN** REPL is invoked with `--no-stream` flag
- **THEN** streaming mode SHALL be disabled
- **AND** REPL SHALL wait for complete response before displaying

## REMOVED Requirements

### Requirement: REPL uses no_stream parameter

**Reason**: Parameter renamed to `stream` with inverted default for clearer CLI flags.

**Migration**: Use `stream: bool = True` instead of `no_stream: bool = False`. The CLI flags are now `--stream` (default) and `--no-stream` (to disable).
