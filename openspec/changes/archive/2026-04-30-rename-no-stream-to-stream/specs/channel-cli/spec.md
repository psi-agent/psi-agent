## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: CLI uses no_stream parameter

**Reason**: Parameter renamed to `stream` with inverted default for clearer CLI flags.

**Migration**: Use `stream: bool = True` instead of `no_stream: bool = False`. The CLI flags are now `--stream` (default) and `--no-stream` (to disable).
