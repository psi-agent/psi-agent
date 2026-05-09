## Tasks

### Phase 1: AI Module Error Path Tests (High Priority)

- [x] T1: Add AI client uninitialized call tests
  - Test `OpenAICompletionsClient.chat_completions()` raises RuntimeError when not initialized
  - Test `AnthropicMessagesClient.messages()` raises RuntimeError when not initialized
  - Files: `tests/ai/openai_completions/test_client.py`, `tests/ai/anthropic_messages/test_client.py`

- [x] T2: Add AI client _handle_error tests
  - Test OpenAI `_handle_error` with `APIStatusError` (status_code present and None)
  - Test OpenAI `_handle_error` with generic `Exception`
  - Test Anthropic `_handle_error` with `APIStatusError`, `APITimeoutError`, and generic `Exception`
  - Files: `tests/ai/openai_completions/test_client.py`, `tests/ai/anthropic_messages/test_client.py`

- [x] T3: Add OpenAI streaming error path tests
  - Test `_stream_request` with `AuthenticationError`, `RateLimitError`, `APIConnectionError`, `APITimeoutError`
  - Verify error JSON chunks are yielded with correct status codes
  - File: `tests/ai/openai_completions/test_client.py`

- [x] T4: Add Anthropic streaming mid-stream error tests
  - Test `_stream_request` with `APITimeoutError`, `APIStatusError`, generic `Exception` mid-stream
  - Verify error JSON chunks are yielded
  - File: `tests/ai/anthropic_messages/test_client.py`

- [x] T5: Add AI server lifecycle tests
  - Test OpenAI server `start()` removes existing socket file
  - Test OpenAI/Anthropic server `stop()` with None client
  - Test Anthropic server `stop()` with None runner
  - Files: `tests/ai/openai_completions/test_server.py`, `tests/ai/anthropic_messages/test_server.py`

### Phase 2: Translator Edge Case Tests (High Priority)

- [x] T6: Add translator invalid tool_call arguments tests
  - Test `_translate_message_to_anthropic` with invalid JSON arguments, None arguments, empty string arguments
  - Verify fallback to `input: {}`
  - File: `tests/ai/anthropic_messages/test_translator.py`

- [x] T7: Add translator None content and unknown format tests
  - Test tool result with None content → empty string
  - Test unknown tool format → pass through unchanged
  - Test assistant message with whitespace-only content and tool_calls → no text block
  - Test empty string content with tool_calls → no text block
  - File: `tests/ai/anthropic_messages/test_translator.py`

- [x] T8: Add translator Anthropic response missing fields tests
  - Test response with no usage → default 0 tokens
  - Test response with no stop_reason → default "end_turn"
  - Test response with unknown stop_reason → default "stop"
  - Test response with no id → empty string
  - Test response with no model → empty string
  - Test response with empty content list → None content
  - File: `tests/ai/anthropic_messages/test_translator.py`

- [x] T9: Add translator SSE stream edge case tests
  - Test SSE event missing event line → skip
  - Test empty stream → no output
  - Test ping event → skip
  - Test multiple system messages → first extracted, rest kept
  - File: `tests/ai/anthropic_messages/test_translator.py`

### Phase 3: Session Core Logic Tests (High Priority)

- [x] T10: Add session multi-round tool call tests
  - Test `_run_conversation` with two rounds of tool calls
  - Test tool call with tool not in registry → error message, conversation continues
  - Test tool call with invalid JSON arguments → error message, conversation continues
  - File: `tests/session/test_runner.py`

- [x] T11: Add session workspace change detection tests
  - Test tools removed → unregistered from registry
  - Test skills changed when system is None → cache set to None
  - Test schedules changed when executor is None → no exception
  - Test simultaneous tools, skills, and schedules changes → all applied
  - File: `tests/session/test_runner.py`

- [x] T12: Add session _complete_fn and streaming tests
  - Test `_complete_fn` with None content → empty string
  - Test `_stream_conversation` with reasoning content → thinking block tags
  - Test `_stream_conversation` with both reasoning and content
  - Test `_stream_conversation` with multiple rounds of tool calls
  - File: `tests/session/test_runner.py`

- [x] T13: Add session _load_single_schedule error tests
  - Test with non-existent directory → None
  - Test with invalid TASK.md → None
  - File: `tests/session/test_runner.py`

### Phase 4: Server Request Handling Tests (High Priority)

- [x] T14: Add server null content and missing fields tests
  - Test `_handle_chat_completions` with user_message content None (xfail if bug exists)
  - Test `_handle_chat_completions` with user_message content empty string
  - Test `_filter_for_channel` with no choices key, empty choices, missing message, None content
  - File: `tests/session/test_server.py`

- [x] T15: Add server start/stop exception tests
  - Test double stop → no exception
  - Test runner __aenter__ raises exception → propagates
  - Test runner __aexit__ raises exception → logged
  - File: `tests/session/test_server.py`

### Phase 5: Schedule Executor Edge Tests (Medium Priority)

- [x] T16: Add schedule executor exception and retry tests
  - Test `_schedule_loop` exception → sleep 60s and retry
  - Test `CancelledError` → clean exit
  - Test immediate execution when next run is due (0 seconds)
  - File: `tests/session/schedule/test_schedule.py`

- [x] T17: Add schedule executor concurrent operation tests
  - Test add schedule with duplicate name
  - Test add schedule when executor not running
  - Test remove schedule that is currently executing
  - Test update schedule that is currently executing
  - File: `tests/session/schedule/test_schedule.py`

- [x] T18: Add schedule executor double start/stop tests
  - Test double start → no duplicate tasks
  - Test double stop → no exception
  - File: `tests/session/schedule/test_schedule.py`

- [x] T19: Add schedule parse_frontmatter edge case tests
  - Test invalid cron expression → exception from croniter
  - Test frontmatter with blank lines between key-value pairs
  - Test frontmatter value containing hash character
  - File: `tests/session/schedule/test_loader.py`

### Phase 6: Manifest Validation Tests (Medium Priority)

- [x] T20: Add manifest parse validation tests
  - Test layer data not dict → ManifestParseError
  - Test invalid parent UUID → ManifestParseError
  - Test tag not string → ManifestParseError
  - Test default invalid UUID → ManifestParseError
  - Test layer with empty dict → success
  - Test tag explicitly null → success with None
  - File: `tests/workspace/test_manifest.py`

- [x] T21: Add manifest resolve_chain and edge case tests
  - Test resolve_chain with broken chain → ValueError
  - Test get_children with missing UUID → empty list
  - Test get_root_layers with multiple roots
  - Test lookup_by_tag with empty string → ManifestParseError
  - Test serialize_manifest with default=None (xfail if bug exists)
  - Test ManifestParseError with details
  - File: `tests/workspace/test_manifest.py`

### Phase 7: Workspace Operation Tests (Medium Priority)

- [x] T22: Add pack and unpack error path tests
  - Test pack with mksquashfs failure → PackError
  - Test pack with empty directory → success
  - Test unpack with corrupt file → UnpackError
  - Test unpack with empty file → UnpackError
  - Test unpack with existing output directory
  - Test PackError and UnpackError message preservation
  - Files: `tests/workspace/test_pack.py`, `tests/workspace/test_unpack.py`

- [x] T23: Add umount and snapshot error path tests
  - Test umount with missing squashfs_mount key → UmountError (xfail if KeyError bug)
  - Test umount with missing upper_dir key → UmountError (xfail if KeyError bug)
  - Test _cleanup_directory with read-only files
  - Test snapshot with missing upper_dir key → SnapshotError (xfail if KeyError bug)
  - Test snapshot with different output_file from input_file
  - Test snapshot with output_file that already exists
  - Test snapshot manifest updates (parent = previous default, default = new layer)
  - Files: `tests/workspace/test_umount.py`, `tests/workspace/test_snapshot_api.py`

- [x] T24: Add mount _resolve_target_layer edge case test
  - Test valid UUID format but not in layers → tag lookup fallback → MountError
  - File: `tests/workspace/test_mount_api.py`

### Phase 8: Channel SSE Tests (Medium Priority)

- [x] T25: Add channel client null/empty content tests
  - Test ReplClient null content in delta → skip
  - Test TelegramClient null content in delta → skip
  - Test CliClient empty string content → handled
  - Test all clients null content in non-streaming response → empty string
  - Test all clients missing choices in response → error or empty string
  - Files: `tests/channel/repl/test_client.py`, `tests/channel/cli/test_client.py`, `tests/channel/telegram/test_client.py`

- [x] T26: Add channel client reasoning and missing field tests
  - Test ReplClient reasoning field → handled
  - Test TelegramClient reasoning field → handled
  - Test all clients empty choices list → skip
  - Test all clients missing delta key → no crash
  - Files: `tests/channel/repl/test_client.py`, `tests/channel/cli/test_client.py`, `tests/channel/telegram/test_client.py`

- [x] T27: Add TelegramClient user_id tests
  - Test send_message includes user field in request body
  - Test send_message_stream includes user field in request body
  - File: `tests/channel/telegram/test_client.py`

### Phase 9: Telegram Bot Tests (Low Priority)

- [x] T28: Add TelegramBot _stop and split_message tests
  - Test _stop with running application
  - Test _stop when app is None
  - Test split_message with newline exactly at midpoint
  - Test split_message with space exactly at midpoint
  - Test split_message with very small max_length
  - File: `tests/channel/telegram/test_bot_streaming.py`

- [x] T29: Add TelegramBot streaming and handler tests
  - Test streaming with empty content_buffer and non-empty response → fallback
  - Test streaming error cancels typing indicator
  - Test non-streaming with 3+ split chunks
  - Test start without proxy
  - Test start registers handlers
  - File: `tests/channel/telegram/test_bot_streaming.py`

### Phase 10: Workspace CLI Tests (Low Priority)

- [x] T30: Add workspace pack/unpack CLI tests
  - Test Pack __call__ calls pack() API
  - Test Pack main calls tyro.cli
  - Test Unpack __call__ calls unpack() API
  - Test Unpack main calls tyro.cli
  - Files: `tests/workspace/test_pack_cli.py` (new), `tests/workspace/test_unpack_cli.py` (new)

- [x] T31: Add workspace mount/umount CLI tests
  - Test Mount __call__ calls mount() API
  - Test Mount main calls tyro.cli
  - Test Umount __call__ calls umount() API
  - Test Umount main calls tyro.cli
  - Files: `tests/workspace/test_mount_cli.py` (new), `tests/workspace/test_umount_cli.py` (new)

- [x] T32: Add workspace snapshot CLI tests
  - Test Snapshot __call__ calls snapshot() API
  - Test Snapshot main calls tyro.cli
  - File: `tests/workspace/test_snapshot_cli.py` (new)
