## MODIFIED Requirements

### Requirement: system.py exports System class

The `systems/system.py` file SHALL export a `System` class that encapsulates all system configuration and state management.

#### Scenario: System class instantiation
- **WHEN** session starts
- **THEN** it instantiates a `System` object with the workspace directory
- **AND** the `System` object manages internal state across method calls

### Requirement: System class provides build_system_prompt method

The `System` class SHALL provide an async `build_system_prompt()` method that constructs the system prompt.

#### Scenario: build_system_prompt method
- **WHEN** `build_system_prompt()` is called on a `System` instance
- **THEN** it returns a system prompt string
- **AND** it accepts optional parameters for customization

### Requirement: System class provides compact_history method

The `System` class SHALL provide an async `compact_history()` method that compacts conversation history.

#### Scenario: compact_history method
- **WHEN** `compact_history()` is called on a `System` instance
- **THEN** it accepts history, complete_fn, and optional parameters
- **AND** it returns compacted history

### Requirement: System class manages previous_summary state

The `System` class SHALL internally manage `previous_summary` state for incremental summary updates.

#### Scenario: First compaction
- **WHEN** `compact_history()` is called for the first time
- **THEN** no previous summary exists
- **AND** a new summary is generated from scratch

#### Scenario: Subsequent compaction
- **WHEN** `compact_history()` is called after a previous compaction
- **THEN** the previous summary is used for incremental update
- **AND** the new summary preserves information from the previous summary

### Requirement: message serialization handles all block types

The message serialization SHALL handle `thinking`, `toolCall`, and `toolResult` blocks in addition to text content.

#### Scenario: Thinking blocks
- **WHEN** serializing a message with thinking content
- **THEN** the thinking content is labeled as `[Assistant thinking]:`

#### Scenario: Tool call blocks
- **WHEN** serializing a message with tool calls
- **THEN** each tool call is formatted as `tool_name(arg1=value1, ...)`
- **AND** labeled as `[Assistant tool calls]:`

#### Scenario: Tool result blocks
- **WHEN** serializing a tool result
- **THEN** the content is labeled as `[Tool result]:`
- **AND** truncated to a maximum of 2000 characters

### Requirement: summarization uses dedicated system prompt

The summarization function SHALL use a dedicated system prompt that instructs the LLM to only output the structured summary and not continue the conversation.

#### Scenario: System prompt prevents conversation continuation
- **WHEN** generating a summary
- **THEN** the system prompt instructs the LLM to NOT continue the conversation
- **AND** the system prompt instructs the LLM to NOT respond to questions
- **AND** the system prompt instructs the LLM to ONLY output the structured summary
