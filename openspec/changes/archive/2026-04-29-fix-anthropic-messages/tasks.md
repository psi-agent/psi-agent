## 1. Request Translation

- [x] 1.1 Create `translator.py` module with `translate_openai_to_anthropic()` function
- [x] 1.2 Implement system message extraction (role="system" → system parameter)
- [x] 1.3 Implement message content conversion (string → content block array)
- [x] 1.4 Add unit tests for request translation

## 2. Response Translation

- [x] 2.1 Implement `translate_anthropic_to_openai()` function for non-streaming responses
- [x] 2.2 Map Anthropic response fields to OpenAI format (id, choices, usage)
- [x] 2.3 Add unit tests for response translation

## 3. Streaming Translation

- [x] 3.1 Implement streaming event parser for Anthropic SSE events
- [x] 3.2 Convert `content_block_delta` events to OpenAI chunks
- [x] 3.3 Handle `message_start`, `message_stop` events
- [x] 3.4 Add unit tests for streaming translation

## 4. Server Updates

- [x] 4.1 Change endpoint from `/v1/messages` to `/v1/chat/completions`
- [x] 4.2 Integrate request translation in server handler
- [x] 4.3 Update server tests for new endpoint and format

## 5. Client Updates

- [x] 5.1 Integrate response translation in client
- [x] 5.2 Update streaming to emit OpenAI format chunks
- [x] 5.3 Update client tests for new format

## 6. Integration Testing

- [x] 6.1 Test end-to-end request flow with mock Anthropic API
- [x] 6.2 Test streaming mode end-to-end
- [x] 6.3 Verify error handling preserves OpenAI format

## 7. Documentation

- [x] 7.1 Update spec files in `openspec/specs/` with delta changes
- [x] 7.2 Update any relevant README or usage documentation
