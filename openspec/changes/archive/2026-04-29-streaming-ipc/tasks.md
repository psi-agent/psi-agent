## 1. Channel Client Streaming Support

- [x] 1.1 Add `send_message_stream()` method to `ReplClient` class in `src/psi_agent/channel/repl/client.py`
- [x] 1.2 Implement SSE parsing logic for streaming responses
- [x] 1.3 Add callback parameter for real-time chunk processing
- [x] 1.4 Update existing `send_message()` to keep non-streaming behavior

## 2. REPL Real-time Display

- [x] 2.1 Update `repl.py` to use `send_message_stream()` by default
- [x] 2.2 Implement real-time output display for streaming chunks
- [x] 2.3 Handle `[DONE]` marker to finalize display
- [x] 2.4 Add option to switch between streaming/non-streaming mode

## 3. Session Default Streaming

- [x] 3.1 Modify `_run_conversation()` in `runner.py` to use streaming by default
- [x] 3.2 Implement internal collection of streaming chunks for tool call handling
- [x] 3.3 Ensure tool call reconstruction works with collected streaming data
- [x] 3.4 Update `_run_streaming_conversation()` to handle both modes cleanly

## 4. Session Response Forwarding

- [x] 4.1 Update `_handle_chat_completions()` in `server.py` to default `stream: true`
- [x] 4.2 Ensure streaming response forwarding hides tool_calls properly
- [x] 4.3 Verify non-streaming mode still works when explicitly requested

## 5. Testing

- [x] 5.1 Add unit tests for `ReplClient.send_message_stream()`
- [x] 5.2 Add unit tests for streaming chunk parsing
- [x] 5.3 Add integration tests for Channel → Session → AI streaming flow
- [x] 5.4 Add tests for tool call handling with streaming responses
- [x] 5.5 Run full test suite to verify no regressions

## 6. Documentation and Quality

- [x] 6.1 Update CLAUDE.md if needed for new streaming behavior
- [x] 6.2 Run `ruff check` and `ruff format` on all modified files
- [x] 6.3 Run `ty check` for type safety verification