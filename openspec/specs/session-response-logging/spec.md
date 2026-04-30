## ADDED Requirements

### Requirement: Session logs all AI response fields

Session SHALL log all non-empty fields from AI streaming response chunks at DEBUG level, without truncation.

#### Scenario: Content field is present
- **WHEN** AI returns a streaming chunk with `content` field
- **THEN** Session SHALL log the complete content without truncation

#### Scenario: Tool calls field is present
- **WHEN** AI returns a streaming chunk with `tool_calls` field
- **THEN** Session SHALL log the tool call information including function name and arguments

#### Scenario: Reasoning content field is present
- **WHEN** AI returns a streaming chunk with `reasoning_content` or similar thinking field
- **THEN** Session SHALL log the complete reasoning content

#### Scenario: Field is null or missing
- **WHEN** AI returns a streaming chunk with null or missing field
- **THEN** Session SHALL skip logging that field without error

### Requirement: Defensive logging for null values

All logging code SHALL use defensive null checks before accessing response fields.

#### Scenario: Delta content is null
- **WHEN** streaming delta has `content: null`
- **THEN** logging code SHALL skip content logging without crash

#### Scenario: Tool calls array is empty
- **WHEN** streaming delta has `tool_calls: []`
- **THEN** logging code SHALL skip tool calls logging
