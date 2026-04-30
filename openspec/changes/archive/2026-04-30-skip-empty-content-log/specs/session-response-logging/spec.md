## MODIFIED Requirements

### Requirement: Session logs all AI response fields

Session SHALL log all non-empty fields from AI streaming response chunks at DEBUG level, without truncation.

#### Scenario: Content field is present and non-empty
- **WHEN** AI returns a streaming chunk with non-empty `content` field
- **THEN** Session SHALL log the complete content without truncation

#### Scenario: Content field is empty string
- **WHEN** AI returns a streaming chunk with `content: ""`
- **THEN** Session SHALL skip logging the content field

#### Scenario: Content field is null
- **WHEN** AI returns a streaming chunk with `content: null`
- **THEN** Session SHALL skip logging the content field

#### Scenario: Tool calls field is present
- **WHEN** AI returns a streaming chunk with `tool_calls` field
- **THEN** Session SHALL log the tool call information including function name and arguments

#### Scenario: Reasoning field is present and non-empty
- **WHEN** AI returns a streaming chunk with non-empty `reasoning` field
- **THEN** Session SHALL log the complete reasoning content

#### Scenario: Reasoning field is empty or null
- **WHEN** AI returns a streaming chunk with empty or null `reasoning` field
- **THEN** Session SHALL skip logging the reasoning field

### Requirement: Defensive logging for null values

All logging code SHALL use defensive null checks before accessing response fields.

#### Scenario: Delta content is null
- **WHEN** streaming delta has `content: null`
- **THEN** logging code SHALL skip content logging without crash

#### Scenario: Tool calls array is empty
- **WHEN** streaming delta has `tool_calls: []`
- **THEN** logging code SHALL skip tool calls logging
