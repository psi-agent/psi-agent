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
