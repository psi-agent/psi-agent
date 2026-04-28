## ADDED Requirements

### Requirement: Orphaned tool results are removed during compaction

When conversation history is compacted, tool_result messages without corresponding tool_use blocks SHALL be removed to prevent API errors.

#### Scenario: Tool use removed but result kept
- **WHEN** an assistant message with tool_use is removed during compaction
- **AND** the corresponding tool_result message remains
- **THEN** the orphaned tool_result SHALL be removed from the compacted history

#### Scenario: Multiple orphaned results
- **WHEN** multiple tool_result messages exist without matching tool_use blocks
- **THEN** all orphaned tool_result messages SHALL be removed

### Requirement: Duplicate tool results are removed

When the same tool_call_id appears in multiple tool_result messages, only the first occurrence SHALL be kept.

#### Scenario: Duplicate tool result IDs
- **WHEN** two tool_result messages have the same tool_call_id
- **THEN** only the first tool_result SHALL be kept
- **AND** subsequent duplicates SHALL be removed

### Requirement: Tool results are matched to tool calls by ID

Tool_result messages SHALL be matched to tool_use blocks using the tool_call_id field.

#### Scenario: Correct ID matching
- **WHEN** a tool_result has tool_call_id "call_123"
- **AND** an assistant message has a tool_use with id "call_123"
- **THEN** the tool_result SHALL be considered matched and kept

#### Scenario: Mismatched ID
- **WHEN** a tool_result has tool_call_id "call_456"
- **AND** no tool_use with id "call_456" exists in the history
- **THEN** the tool_result SHALL be considered orphaned and removed

### Requirement: Repair function returns report

The repair function SHALL return a report containing the repaired messages and statistics.

#### Scenario: Repair report contents
- **WHEN** repair_tool_use_result_pairing is called
- **THEN** the result SHALL include:
  - messages: the repaired message list
  - dropped_orphan_count: number of orphaned tool results removed
  - dropped_duplicate_count: number of duplicate tool results removed

### Requirement: Integration with compact_history

The repair function SHALL be called at the end of compact_history before returning.

#### Scenario: Automatic repair during compaction
- **WHEN** compact_history is called
- **THEN** tool_use/result pairing repair SHALL be applied to the final result
