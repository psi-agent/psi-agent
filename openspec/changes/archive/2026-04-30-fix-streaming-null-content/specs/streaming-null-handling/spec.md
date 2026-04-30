## ADDED Requirements

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
