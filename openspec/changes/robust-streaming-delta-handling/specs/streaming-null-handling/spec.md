## ADDED Requirements

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
