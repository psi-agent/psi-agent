## MODIFIED Requirements

### Requirement: Translate OpenAI request to Anthropic format

The translator SHALL convert OpenAI chat completions request format to Anthropic Messages format.

#### Scenario: Basic text message translation
- **WHEN** request contains messages with `role` and `content` fields
- **THEN** translator SHALL convert content strings to Anthropic content block arrays

#### Scenario: System message extraction
- **WHEN** request contains a message with `role: "system"`
- **THEN** translator SHALL extract it as the `system` parameter for Anthropic API

#### Scenario: Parameter mapping
- **WHEN** request contains `max_tokens`, `temperature`, or `stream`
- **THEN** translator SHALL pass these parameters unchanged to Anthropic API

#### Scenario: Tools parameter translation
- **WHEN** request contains `tools` array in OpenAI format
- **THEN** translator SHALL convert each tool to Anthropic format:
  - Flatten `function` wrapper (move `name`, `description`, `parameters` to top level)
  - Rename `parameters` field to `input_schema`
  - Remove `type: "function"` field

#### Scenario: Tools parameter passthrough
- **WHEN** request contains `tools` already in Anthropic format (has `input_schema`)
- **THEN** translator SHALL pass tools through unchanged

#### Scenario: Tool result message translation
- **WHEN** request contains a message with `role: "tool"`
- **THEN** translator SHALL convert to Anthropic format:
  - Change role to `"user"`
  - Create content block with `type: "tool_result"`
  - Rename `tool_call_id` to `tool_use_id`
  - Wrap `content` in the tool_result content block

#### Scenario: Assistant message with tool_calls
- **WHEN** request contains an assistant message with `tool_calls` array
- **THEN** translator SHALL convert tool_calls to Anthropic tool_use content blocks:
  - Each tool_call becomes a `{"type": "tool_use", "id": ..., "name": ..., "input": ...}` block
  - The `function.arguments` JSON string is parsed as `input` object

### Requirement: Translate streaming events

The translator SHALL convert Anthropic streaming events to OpenAI chunk format.

#### Scenario: Content delta translation
- **WHEN** Anthropic sends `content_block_delta` event with `delta.type: "text_delta"`
- **THEN** translator SHALL emit OpenAI chunk with `delta.content` containing `delta.text` value

#### Scenario: Thinking delta translation
- **WHEN** Anthropic sends `content_block_delta` event with `delta.type: "thinking_delta"`
- **THEN** translator SHALL emit OpenAI chunk with `delta.reasoning_content` containing `delta.thinking` value

#### Scenario: Input JSON delta translation
- **WHEN** Anthropic sends `content_block_delta` event with `delta.type: "input_json_delta"`
- **THEN** translator SHALL emit OpenAI chunk with `delta.tool_calls` containing partial JSON arguments

#### Scenario: Signature delta handling
- **WHEN** Anthropic sends `content_block_delta` event with `delta.type: "signature_delta"`
- **THEN** translator SHALL NOT emit any output chunk

#### Scenario: Stream completion
- **WHEN** Anthropic sends `message_stop` event
- **THEN** translator SHALL emit OpenAI `data: [DONE]` chunk

#### Scenario: Error during streaming
- **WHEN** Anthropic sends error event during streaming
- **THEN** translator SHALL emit OpenAI error chunk format

### Requirement: Handle content block start events

The translator SHALL process `content_block_start` events for all content block types.

#### Scenario: Text block start
- **WHEN** Anthropic sends `content_block_start` with `content_block.type: "text"`
- **THEN** translator SHALL NOT emit any output chunk (text starts with first delta)

#### Scenario: Tool use block start
- **WHEN** Anthropic sends `content_block_start` with `content_block.type: "tool_use"`
- **THEN** translator SHALL emit OpenAI chunk with `delta.tool_calls` containing tool id and name

#### Scenario: Thinking block start
- **WHEN** Anthropic sends `content_block_start` with `content_block.type: "thinking"`
- **THEN** translator SHALL NOT emit any output chunk (thinking starts with first delta)

#### Scenario: Redacted thinking block start
- **WHEN** Anthropic sends `content_block_start` with `content_block.type: "redacted_thinking"`
- **THEN** translator SHALL NOT emit any output chunk and SHALL log debug message

### Requirement: Handle content block stop events

The translator SHALL process `content_block_stop` events to clean up state.

#### Scenario: Tool use block stop
- **WHEN** Anthropic sends `content_block_stop` for a tool use block
- **THEN** translator SHALL clean up pending tool call state

#### Scenario: Other block stop
- **WHEN** Anthropic sends `content_block_stop` for non-tool block
- **THEN** translator SHALL NOT emit any output chunk
