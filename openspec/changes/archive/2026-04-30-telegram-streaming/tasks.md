## 1. Configuration Updates

- [x] 1.1 Update `TelegramConfig` dataclass to add `stream` (bool, default True) and `stream_interval` (float, default 1.0) fields
- [x] 1.2 Update `cli.py` to add `--no-stream` and `--stream-interval` CLI arguments following REPL channel pattern

## 2. Client Streaming Support

- [x] 2.1 Add `send_message_stream()` method to `TelegramClient` with SSE parsing (reference `ReplClient.send_message_stream()`)
- [x] 2.2 Add `on_chunk` callback parameter to `send_message_stream()` for real-time chunk delivery

## 3. Bot Streaming Implementation

- [x] 3.1 Implement streaming message handler in `TelegramBot._handle_message()` that uses `send_message_stream()`
- [x] 3.2 Implement time-based buffering logic to accumulate chunks and edit messages at configured intervals
- [x] 3.3 Handle first chunk by sending initial message, subsequent chunks by editing
- [x] 3.4 Handle message length exceeding 4096 characters during streaming (truncate display, send remainder on completion)
- [x] 3.5 Implement non-streaming fallback when `--no-stream` is set

## 4. Testing

- [x] 4.1 Add unit tests for `TelegramConfig` with new fields
- [x] 4.2 Add unit tests for `TelegramClient.send_message_stream()` method
- [x] 4.3 Add unit tests for streaming buffer logic in `TelegramBot`
- [x] 4.4 Add integration test for streaming message editing flow

## 5. Documentation

- [x] 5.1 Update `openspec/specs/telegram-channel/spec.md` with new streaming requirements
