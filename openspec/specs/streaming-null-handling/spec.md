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
