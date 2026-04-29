## ADDED Requirements

### Requirement: Translator functions are tested
The Anthropic-to-OpenAI translator module SHALL have comprehensive test coverage for all translation functions.

#### Scenario: Translate Anthropic message to OpenAI format
- **WHEN** an Anthropic message with content blocks is translated
- **THEN** the output SHALL be valid OpenAI message format

#### Scenario: Translate OpenAI message to Anthropic format
- **WHEN** an OpenAI message is translated to Anthropic format
- **THEN** the output SHALL be valid Anthropic message format

#### Scenario: Handle empty content
- **WHEN** a message with empty content is translated
- **THEN** the translator SHALL handle it gracefully without error

### Requirement: History compaction is tested
The history compaction module SHALL have test coverage for all compaction scenarios.

#### Scenario: Compact history within limit
- **WHEN** history is within token limit
- **THEN** history SHALL remain unchanged

#### Scenario: Compact history exceeding limit
- **WHEN** history exceeds token limit
- **THEN** older messages SHALL be summarized

### Requirement: Tool loader is tested
The tool loader module SHALL have test coverage for loading, reloading, and error scenarios.

#### Scenario: Load valid tool
- **WHEN** a valid tool Python file is loaded
- **THEN** the tool SHALL be registered correctly

#### Scenario: Handle invalid tool
- **WHEN** an invalid tool file is encountered
- **THEN** the loader SHALL log error and skip the file

#### Scenario: Reload changed tool
- **WHEN** a tool file is modified
- **THEN** the loader SHALL detect and reload the tool

### Requirement: Server request handling is tested
The OpenAI completions server SHALL have test coverage for request handling scenarios.

#### Scenario: Handle valid non-streaming request
- **WHEN** a valid non-streaming request is received
- **THEN** the server SHALL return proper response

#### Scenario: Handle invalid JSON body
- **WHEN** a request with invalid JSON is received
- **THEN** the server SHALL return 400 error

#### Scenario: Handle streaming request
- **WHEN** a streaming request is received
- **THEN** the server SHALL return SSE stream

### Requirement: CLI parameter parsing is tested
All CLI modules SHALL have test coverage for parameter parsing.

#### Scenario: Parse valid CLI arguments
- **WHEN** valid arguments are provided
- **THEN** the CLI SHALL parse them correctly

#### Scenario: Handle missing required argument
- **WHEN** a required argument is missing
- **THEN** the CLI SHALL show error message