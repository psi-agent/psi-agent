## ADDED Requirements

### Requirement: Session streams reasoning field separately

Session SHALL stream reasoning content as a separate `reasoning` field in SSE delta, not embedded in `content`.

#### Scenario: LLM returns reasoning content
- **WHEN** AI returns streaming chunk with `reasoning` field
- **THEN** Session SHALL stream the reasoning content as `reasoning` field in SSE delta

#### Scenario: Tool call is executed
- **WHEN** Session executes a tool call
- **THEN** Session SHALL stream the tool call information (name, arguments, result) as `reasoning` field in SSE delta

#### Scenario: LLM returns content
- **WHEN** AI returns streaming chunk with `content` field
- **THEN** Session SHALL stream the content as `content` field in SSE delta, regardless of whether tool_calls is present

#### Scenario: No reasoning content
- **WHEN** AI returns response without reasoning or tool calls
- **THEN** Session SHALL only stream `content` field, without `reasoning` field

### Requirement: Reasoning field format

The `reasoning` field SHALL contain plain text content without XML-style tags.

#### Scenario: Reasoning content format
- **WHEN** streaming reasoning content from AI
- **THEN** `reasoning` field SHALL contain the raw reasoning text without `<thinking>` tags

#### Scenario: Tool call format
- **WHEN** streaming tool call information
- **THEN** `reasoning` field SHALL contain formatted text like `[Tool: name]\nArguments: {...}\nResult: ...`