## Why

The current Anthropic-to-OpenAI translator has three critical issues:

1. **Tools definition format not translated**: The `translate_openai_to_anthropic` function passes `tools` through unchanged, but OpenAI and Anthropic use different tool definition formats. This causes tools to be ignored by the Anthropic API.

2. **Tool result messages not translated**: When the LLM calls a tool and the session sends back the tool result, it uses OpenAI format (`role: "tool"`). Anthropic doesn't support this role and requires a completely different format.

3. **Thinking content dropped in streaming**: The streaming translator does not handle `thinking` content blocks and `thinking_delta` events introduced in Anthropic's extended thinking API.

### Tool Definition Format Differences

**OpenAI format:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "bash",
        "description": "...",
        "parameters": {"type": "object", ...}
      }
    }
  ]
}
```

**Anthropic format:**
```json
{
  "tools": [
    {
      "name": "bash",
      "description": "...",
      "input_schema": {"type": "object", ...}
    }
  ]
}
```

### Tool Result Message Format Differences

**OpenAI format:**
```json
{
  "role": "tool",
  "tool_call_id": "call_123",
  "content": "Command output here"
}
```

**Anthropic format:**
```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_123",
      "content": "Command output here"
    }
  ]
}
```

Key differences:
- OpenAI uses `role: "tool"`, Anthropic uses `role: "user"`
- OpenAI uses `tool_call_id`, Anthropic uses `tool_use_id`
- Anthropic requires content as array with `type: "tool_result"`

## What Changes

- **Translate `tools` parameter from OpenAI to Anthropic format**:
  - Flatten `function` wrapper
  - Rename `parameters` → `input_schema`
  - Remove `type: "function"` field
- **Translate tool result messages from OpenAI to Anthropic format**:
  - Convert `role: "tool"` to `role: "user"` with `type: "tool_result"` content block
  - Rename `tool_call_id` → `tool_use_id`
  - Wrap content in proper content block structure
- Add support for `thinking` content blocks in streaming
- Add support for `thinking_delta` events in streaming
- Fix `content_block_delta` text handling to check `delta.type` discriminator

## Capabilities

### New Capabilities

- `anthropic-tools-translation`: Translate OpenAI tools format to Anthropic tools format, including function wrapper flattening, `parameters` → `input_schema` renaming, and tool result message conversion.
- `anthropic-thinking-streaming`: Support for Anthropic extended thinking blocks in streaming responses, including `thinking` and `thinking_delta` event translation to OpenAI format.

### Modified Capabilities

- `openai-anthropic-translation`: Extend request translation to handle tools parameter format conversion and tool result message conversion. Extend streaming translation to handle all Anthropic content block types.

## Impact

- **Code**: `src/psi_agent/ai/anthropic_messages/translator.py` - StreamingTranslator class
- **Tests**: `tests/ai/anthropic_messages/test_translator.py` - New test cases for thinking events
- **API**: No breaking changes - thinking content will be added to responses where previously it was dropped
- **Dependencies**: No new dependencies required
