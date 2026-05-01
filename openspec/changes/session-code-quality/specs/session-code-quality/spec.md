## ADDED Requirements

### Requirement: Session module has consistent logging coverage

The session module SHALL log critical operations at appropriate levels:
- Streaming request bodies at DEBUG level
- Tool loading operations at DEBUG level
- Schedule loading operations at DEBUG level
- Streaming response completion at DEBUG level

#### Scenario: Streaming request is logged
- **WHEN** `_stream_conversation` sends a request to AI
- **THEN** a DEBUG log SHALL be emitted with the request body

#### Scenario: Tool loading is logged
- **WHEN** `load_all_tools` loads tools from a directory
- **THEN** a DEBUG log SHALL be emitted indicating which tools are being loaded

#### Scenario: Schedule loading is logged
- **WHEN** `load_schedule` successfully loads a schedule
- **THEN** a DEBUG log SHALL be emitted with the schedule name

#### Scenario: Streaming response completion is logged
- **WHEN** `_handle_streaming` completes a streaming response
- **THEN** a DEBUG log SHALL be emitted indicating completion

### Requirement: Streaming parsing logic is not duplicated

The session module SHALL NOT have duplicate streaming parsing logic between `_run_conversation` and `_stream_conversation` methods.

#### Scenario: Streaming parsing is centralized
- **WHEN** streaming response parsing is needed
- **THEN** a shared helper method SHALL be used to parse SSE chunks
