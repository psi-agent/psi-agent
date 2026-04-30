## 1. Session Runner Streaming

- [x] 1.1 Modify `_stream_conversation` to stream AI's `reasoning` field directly as `reasoning` in SSE delta
- [x] 1.2 Modify `_stream_conversation` to stream tool calls as `reasoning` field (without `<thinking>` tags)
- [x] 1.3 Ensure final content is streamed as `content` field without thinking tags

## 2. Testing and Quality

- [x] 2.1 Run existing test suite to verify no regressions
- [x] 2.2 Run `ruff check` to verify lint passes
- [x] 2.3 Run `ruff format` to verify formatting
- [x] 2.4 Run `ty check` to verify type checking passes