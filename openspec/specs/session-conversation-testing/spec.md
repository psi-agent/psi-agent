## ADDED Requirements

### Requirement: Session handles multiple rounds of tool calls
`SessionRunner._run_conversation` SHALL handle conversations where the LLM makes tool calls that produce further tool calls in subsequent rounds.

#### Scenario: Two rounds of tool calls
- **WHEN** the LLM first returns a tool call, and after receiving the tool result, returns another tool call
- **THEN** both tool calls SHALL be executed, and the final response SHALL include results from both

#### Scenario: Tool call with tool not in registry
- **WHEN** the LLM returns a tool call for a tool name not in the registry
- **THEN** the tool executor SHALL return an error message, and the conversation SHALL continue

#### Scenario: Tool call with invalid JSON arguments
- **WHEN** the LLM returns a tool call with arguments that are not valid JSON
- **THEN** the tool executor SHALL return an error message, and the conversation SHALL continue

### Requirement: Session handles workspace change detection with mixed changes
`SessionRunner._handle_workspace_changes` SHALL handle all combinations of workspace changes correctly.

#### Scenario: Tools removed
- **WHEN** workspace changes include tools that were removed
- **THEN** the removed tools SHALL be unregistered from the tool registry

#### Scenario: Skills changed when system is None
- **WHEN** workspace changes include skills modified and `self._system` is None
- **THEN** the system prompt cache SHALL be set to None

#### Scenario: Schedules changed when executor is None
- **WHEN** workspace changes include schedules modified and `self._schedule_executor` is None
- **THEN** no exception SHALL be raised (schedule changes SHALL be skipped)

#### Scenario: Simultaneous tools, skills, and schedules changes
- **WHEN** workspace changes include tools added/removed, skills modified, and schedules added/removed simultaneously
- **THEN** all changes SHALL be applied in order: tools updated, system prompt cache invalidated, schedules updated

### Requirement: Session _complete_fn handles None content
`SessionRunner._complete_fn` SHALL handle LLM responses where `message.content` is `None`.

#### Scenario: Response with None content
- **WHEN** the LLM response has `message.content: None`
- **THEN** `_complete_fn` SHALL return an empty string

### Requirement: Session streaming handles reasoning field end-to-end
`SessionRunner._stream_conversation` SHALL correctly stream reasoning content from the AI response.

#### Scenario: Streaming with reasoning content
- **WHEN** the streaming response includes reasoning content in delta
- **THEN** the reasoning content SHALL be formatted with thinking block tags and yielded

#### Scenario: Streaming with both reasoning and content
- **WHEN** the streaming response includes both reasoning and content in the same chunk
- **THEN** both SHALL be yielded in the correct format

### Requirement: Session streaming handles multiple rounds of tool calls
`SessionRunner._stream_conversation` SHALL handle streaming conversations with multiple rounds of tool calls.

#### Scenario: Streaming with two rounds of tool calls
- **WHEN** the streaming response includes tool calls, and after tool execution, the next streaming response includes more tool calls
- **THEN** all tool calls SHALL be executed and results streamed

### Requirement: Session _load_single_schedule handles errors
`SessionRunner._load_single_schedule` SHALL handle errors when loading a schedule.

#### Scenario: Task directory does not exist
- **WHEN** `_load_single_schedule` is called with a non-existent directory
- **THEN** it SHALL return None

#### Scenario: Task directory with invalid TASK.md
- **WHEN** `_load_single_schedule` is called with a directory containing an invalid TASK.md
- **THEN** it SHALL return None
