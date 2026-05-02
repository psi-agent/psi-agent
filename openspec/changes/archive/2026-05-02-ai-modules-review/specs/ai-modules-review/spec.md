## ADDED Requirements

### Protocol Translation Correctness

**REQ-1**: Non-streaming Anthropic responses must include `tool_calls` in the message when `stop_reason` is `"tool_use"`.

When Anthropic returns a response with `tool_use` content blocks:
- The `finish_reason` must be `"tool_calls"`
- The `message.tool_calls` field must be populated with the tool calls
- Each tool call must have `id`, `type: "function"`, and `function.name` and `function.arguments`

**Rationale**: This ensures parity with OpenAI responses and the streaming Anthropic translation which already handles this correctly.

### Error Handling

**REQ-2**: Streaming error chunks must be handled visibly, not silently ignored.

When an AI module yields `{"error": "...", "status_code": ...}` during streaming:
- The error must be logged at ERROR level
- The session must not silently continue with empty content
- The user must receive an error indication

## REMOVED Requirements

None - this is a bug fix and improvement with no removed functionality.

## MODIFIED Requirements

None - existing behavior is preserved except for the bug fix.