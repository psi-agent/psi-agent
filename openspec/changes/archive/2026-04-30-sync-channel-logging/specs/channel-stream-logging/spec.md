## ADDED Requirements

### Requirement: Channel logs all AI response fields

Channel SHALL log all non-empty fields from AI streaming response chunks at DEBUG level, without truncation.

#### Scenario: Reasoning field is present and non-empty
- **WHEN** Channel receives a streaming chunk with non-empty `reasoning` field
- **THEN** Channel SHALL log `Stream reasoning chunk: {content}` with the complete reasoning content

#### Scenario: Content field is present and non-empty
- **WHEN** Channel receives a streaming chunk with non-empty `content` field
- **THEN** Channel SHALL log `Stream content chunk: {content}` with the complete content

#### Scenario: Content field is empty string
- **WHEN** Channel receives a streaming chunk with `content: ""`
- **THEN** Channel SHALL skip logging the content field

#### Scenario: Content field is null
- **WHEN** Channel receives a streaming chunk with `content: null`
- **THEN** Channel SHALL skip logging the content field

#### Scenario: Reasoning field is empty or null
- **WHEN** Channel receives a streaming chunk with empty or null `reasoning` field
- **THEN** Channel SHALL skip logging the reasoning field

### Requirement: Defensive logging for null values

All channel logging code SHALL use defensive null checks before accessing response fields.

#### Scenario: Delta content is null
- **WHEN** streaming delta has `content: null`
- **THEN** logging code SHALL skip content logging without crash

#### Scenario: Delta reasoning is null
- **WHEN** streaming delta has `reasoning: null`
- **THEN** logging code SHALL skip reasoning logging without crash
