## 1. Update openai_completions module

- [x] 1.1 Add DEBUG log for request body in `_stream_request` method of client.py
- [x] 1.2 Add DEBUG log for streaming completion in `_handle_streaming` method of server.py
- [x] 1.3 Remove redundant assert in `start` method of server.py

## 2. Update anthropic_messages module

- [x] 2.1 Add DEBUG log for request body in `_stream_request` method of client.py
- [x] 2.2 Add DEBUG log for streaming completion in `_handle_streaming` method of server.py
- [x] 2.3 Remove redundant assert in `start` method of server.py
- [x] 2.4 Fix `translate_anthropic_to_openai` to extract tool_use content blocks and populate `message.tool_calls`

## 3. Update session module for streaming error handling

- [x] 3.1 Handle error chunks in `_parse_streaming_response` method of runner.py - detect `{"error": ...}` format and raise exception or log appropriately instead of silently ignoring

## 4. Add tests for tool_calls translation fix

- [x] 4.1 Add test for `translate_anthropic_to_openai` with tool_use content blocks
- [x] 4.2 Add test for `translate_anthropic_to_openai` with mixed text and tool_use blocks
