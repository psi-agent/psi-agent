## 1. Update StreamingTranslator for thinking support

- [x] 1.1 Add `_make_chunk` support for `reasoning_content` parameter
- [x] 1.2 Add tracking for redacted thinking blocks (set of indices to skip)
- [x] 1.3 Handle `content_block_start` for `thinking` type (no output, no tracking needed)
- [x] 1.4 Handle `content_block_start` for `redacted_thinking` type (add to skip set, log debug)
- [x] 1.5 Handle `thinking_delta` in `content_block_delta` (emit reasoning_content chunk)
- [x] 1.6 Handle `signature_delta` in `content_block_delta` (no output)
- [x] 1.7 Update `content_block_stop` to clean up redacted thinking skip set

## 2. Fix text delta handling

- [x] 2.1 Update `content_block_delta` to check `delta.type == "text_delta"` first
- [x] 2.2 Access `delta.text` for text_delta type (not `delta.get("text")`)
- [x] 2.3 Maintain backward compatibility with raw JSON events

## 3. Add tools format translation

- [x] 3.1 Add `_translate_tools_to_anthropic` helper function
- [x] 3.2 Flatten `function` wrapper in tool definitions
- [x] 3.3 Rename `parameters` to `input_schema`
- [x] 3.4 Handle tools already in Anthropic format (passthrough)
- [x] 3.5 Call tools translation in `translate_openai_to_anthropic`

## 4. Add tests for tools translation

- [x] 4.1 Test OpenAI tools format translation
- [x] 4.2 Test Anthropic tools format passthrough
- [x] 4.3 Test tools without description field

## 5. Add comprehensive tests for thinking

- [x] 5.1 Test `thinking` block start event (no output)
- [x] 5.2 Test `thinking_delta` event produces `reasoning_content` chunk
- [x] 5.3 Test `signature_delta` event produces no output
- [x] 5.4 Test `redacted_thinking` block start (skip with debug log)
- [x] 5.5 Test multiple `thinking_delta` events in sequence
- [x] 5.6 Test `text_delta` with proper type discriminator
- [x] 5.7 Test full stream with thinking content followed by text content
- [x] 5.8 Test full stream with tool calls and thinking mixed

## 6. Run quality checks

- [x] 6.1 Run `ruff check` and fix lint issues
- [x] 6.2 Run `ruff format` and ensure formatting
- [x] 6.3 Run `ty check` and fix type errors
- [x] 6.4 Run `pytest` and ensure all tests pass

## 7. Add tool result message translation

- [x] 7.1 Add `_translate_message_to_anthropic` helper function
- [x] 7.2 Convert `role: "tool"` to `role: "user"` with `tool_result` content block
- [x] 7.3 Rename `tool_call_id` to `tool_use_id`
- [x] 7.4 Handle assistant messages with `tool_calls` (convert to tool_use blocks)
- [x] 7.5 Integrate into message translation loop

## 8. Add tests for tool result translation

- [x] 8.1 Test tool result message translation
- [x] 8.2 Test assistant message with tool_calls translation
- [x] 8.3 Test tool result with non-string content

## 9. Run final quality checks

- [x] 9.1 Run `ruff check` and fix lint issues
- [x] 9.2 Run `ruff format` and ensure formatting
- [x] 9.3 Run `ty check` and fix type errors
- [x] 9.4 Run `pytest` and ensure all tests pass
