## ADDED Requirements

### Requirement: Streaming delta null value handling

The session component SHALL gracefully handle null values in streaming delta fields that expect iterable types.

#### Scenario: tool_calls field is null
- **WHEN** LLM provider returns a streaming delta with `tool_calls: null`
- **THEN** the session SHALL skip processing tool calls without crashing

#### Scenario: tool_calls field is missing
- **WHEN** LLM provider returns a streaming delta without `tool_calls` field
- **THEN** the session SHALL skip processing tool calls without crashing

#### Scenario: tool_calls field has valid data
- **WHEN** LLM provider returns a streaming delta with valid `tool_calls` array
- **THEN** the session SHALL process tool calls normally

### Requirement: Streaming handles null content in delta

The session runner SHALL handle streaming delta objects where `content` is `null` without crashing.

#### Scenario: Tool call with null content
- **WHEN** LLM returns a streaming delta with `content: null` and `tool_calls` present
- **THEN** session continues processing without TypeError

#### Scenario: Empty string content
- **WHEN** LLM returns a streaming delta with `content: ""`
- **THEN** session logs the empty content and continues normally

#### Scenario: Normal text content
- **WHEN** LLM returns a streaming delta with actual text content
- **THEN** session logs first 100 characters and processes content normally

### Requirement: Tool calls reconstruction handles null name field

The `_reconstruct_tool_calls` method SHALL handle `name: null` in tool call delta chunks without crashing.

#### Scenario: Subsequent chunk with null name
- **WHEN** LLM returns a streaming tool call delta with `function.name: null`
- **THEN** session continues processing without TypeError

#### Scenario: Subsequent chunk with missing name field
- **WHEN** LLM returns a streaming tool call delta without `name` field in function
- **THEN** session continues processing without TypeError

#### Scenario: First chunk with valid name
- **WHEN** LLM returns a streaming tool call delta with valid `function.name`
- **THEN** session accumulates the name correctly

### Requirement: Tool calls reconstruction handles null arguments field

The `_reconstruct_tool_calls` method SHALL handle `arguments: null` in tool call delta chunks without crashing.

#### Scenario: Chunk with null arguments
- **WHEN** LLM returns a streaming tool call delta with `function.arguments: null`
- **THEN** session continues processing without TypeError

#### Scenario: Chunk with valid arguments
- **WHEN** LLM returns a streaming tool call delta with valid `function.arguments`
- **THEN** session accumulates the arguments correctly
