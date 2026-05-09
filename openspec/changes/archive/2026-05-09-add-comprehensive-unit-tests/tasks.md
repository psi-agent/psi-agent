## 1. Session Types Happy Path (NEW test file)

- [x] 1.1 Create tests/session/test_types.py with ToolSchema construction tests
- [x] 1.2 Add ToolRegistry happy path tests: register tool, get registered tool, unregister tool, list_tools returns schemas, clear empties registry, register multiple tools
- [x] 1.3 Add History happy path tests: construct with messages, add_message, get messages, clear

## 2. Session Config Happy Path (NEW test file)

- [x] 2.1 Create tests/session/test_config.py with SessionConfig construction tests
- [x] 2.2 Add all helper method tests: channel_socket_path, ai_socket_path, workspace_path, history_file_path (None and non-None), tools_dir, systems_dir

## 3. Session Runner Happy Path

- [x] 3.1 Add _load_system() tests: load System class with build_system_prompt and compact_history, load System class without required methods
- [x] 3.2 Add _handle_workspace_changes schedule branch tests: schedules_added triggers add_schedule, schedules_modified triggers update_schedule, schedules_removed triggers remove_schedule
- [x] 3.3 Add _build_messages with System instance test: compact_history path is called when System instance is available

## 4. Session Schedule Happy Path

- [x] 4.1 Add ScheduleExecutor._execute_task normal success path test
- [x] 4.2 Add ScheduleExecutor._schedule_loop basic behavior test (using short delay and mock runner)

## 5. Channel Cli Client Happy Path

- [x] 5.1 Add CliClient._send_non_streaming success path test (mock aiohttp response)
- [x] 5.2 Add CliClient._send_streaming success path test (mock SSE response)
- [x] 5.3 Add CliClient.send_message dispatches to streaming/non-streaming based on config

## 6. Session Types Corner Cases

- [x] 6.1 Add ToolRegistry corner case tests: register duplicate tool (verify overwrite behavior), unregister nonexistent tool (verify no exception), get nonexistent tool (verify returns None), list_tools on empty registry
- [x] 6.2 Add History corner case tests: add_message with various roles, verify messages order preservation, clear and verify empty, History with pre-populated messages

## 7. Session Config Corner Cases

- [x] 7.1 Add SessionConfig corner case tests: history_file_path with None, workspace with special characters (spaces, unicode)

## 8. Session Tool Loader Corner Cases

- [x] 8.1 Add parse_google_docstring corner case tests: docstring with only Returns section, docstring with only Args section, nested colons in param descriptions, empty docstring, single-line docstring, Unicode content, Args with no space after colon
- [x] 8.2 Add python_type_to_openai_type extended tests: uppercase "List" and "Dict" types, unknown types default to "string", verify all standard type mappings
- [x] 8.3 Add generate_tool_schema boundary tests: function with no parameters, function with all parameters having defaults, function with mixed required/optional parameters
- [x] 8.4 Add load_tool_from_file exception path tests: empty file, file with only comments, tool function missing type annotations

## 9. Session Tool Executor Corner Cases

- [x] 9.1 Add execute_tool exception tests: tool raising TypeError (argument mismatch), tool returning None, tool returning empty string, tool returning non-string types (dict, list)
- [x] 9.2 Add execute_tools_parallel boundary tests: empty tool_calls list, tool_call missing function field, tool_call missing id field, all tool_calls failing

## 10. Session Workspace Watcher Corner Cases

- [x] 10.1 Add WorkspaceWatcher composite change tests: initialize with empty workspace, simultaneous add+modify+remove across tools/skills/schedules, add then immediately remove same tool between checks, modify then modify again (hash updates twice)
- [x] 10.2 Add WorkspaceWatcher idempotency tests: consecutive check_for_changes with no changes returns empty summary, check_for_changes updates internal hashes so subsequent check does not re-report
- [x] 10.3 Add scan directory edge case tests: tools dir with subdirectories, __pycache__ and .pyc files, __init__.py as tool; skills dir with special characters; schedules dir with non-directory entries

## 11. Session History Corner Cases

- [x] 11.1 Add load_history_from_file edge case tests: non-JSON-array content (JSON object, string, number), empty string file, "null" content, valid JSON but not list
- [x] 11.2 Add save_history_to_file edge case tests: messages with non-ASCII characters (ensure_ascii=False preserves), messages with special JSON characters, empty message list saves as "[]"
- [x] 11.3 Add round-trip consistency test: save then load produces identical messages

## 12. Session Schedule Corner Cases

- [x] 12.1 Add parse_frontmatter corner case tests: empty frontmatter (only ---\n---\n), missing closing ---, YAML value containing colons, unknown fields, empty file, content without frontmatter, missing cron field, empty cron string
- [x] 12.2 Add Schedule corner case tests: get_next_run croniter instance reuse (multiple calls return increasing times), invalid cron expression behavior
- [x] 12.3 Add ScheduleExecutor lifecycle tests: add same-name schedule (verify behavior), update nonexistent schedule, add/remove/add same schedule lifecycle, start/stop idempotency

## 13. Session Server Corner Cases

- [x] 13.1 Add _filter_for_channel edge case tests: empty choices list, choices without message field, content as empty string, content as None, message with tool_calls filtered, multiple choices
- [x] 13.2 Add _handle_chat_completions boundary tests: stream=True with uninitialized runner, multiple user messages (verify last one used), request missing required fields

## 14. Session Runner Corner Cases

- [x] 14.1 Add _reconstruct_tool_calls boundary tests: empty list, non-contiguous indices, large index values, function.name as None, multiple tool calls interleaved
- [x] 14.2 Add _parse_streaming_response boundary tests: very long SSE line, content as None delta, tool_calls as None delta, consecutive error chunks, data after [DONE]
- [x] 14.3 Add format functions edge case tests: format_thinking_block with empty string, format_tool_call_thinking with empty result, content with special characters (XML tags)

## 15. Workspace Manifest Corner Cases

- [x] 15.1 Add Manifest graph operation tests: multi-layer chain resolution, tag lookup for nonexistent tag, get_all_tags on empty manifest, default layer not in layers
- [x] 15.2 Add parse_manifest malformed input tests: empty JSON, JSON array (not object), layers not dict, default not in layers, parent references nonexistent UUID, duplicate tags, missing layers/default fields
- [x] 15.3 Add serialize_manifest round-trip tests: parse → serialize → parse consistency, manifest with multiple layers and tags

## 16. Channel Telegram Corner Cases

- [x] 16.1 Add split_message boundary tests: message exactly at max_length, message with only spaces/newlines, unicode at boundary, max_length=1, empty string, max_length+1 message, consecutive newlines, markdown formatting

## 17. Anthropic Translator Corner Cases

- [x] 17.1 Add _translate_message_to_anthropic edge case tests: content as None, content as number, content as empty string, content as list, unknown role, empty tool_calls array, tool_call with invalid JSON arguments, tool_call missing id/function fields
- [x] 17.2 Add translate_openai_to_anthropic boundary tests: multiple system messages (only first extracted), no system message, empty messages list, only system message, empty tools list, max_tokens provided (no default), thinking/reasoning_effort passthrough
- [x] 17.3 Add translate_anthropic_to_openai edge case tests: empty content blocks, unknown stop_reason, no usage field, unknown block type
- [x] 17.4 Add StreamingTranslator edge case tests: unknown event_type returns None, message_start without message field, content_block_delta without delta field, consecutive thinking_delta events, redacted_thinking delta skipping

## 18. Verification

- [x] 18.1 Run all tests and verify they pass: `uv run pytest tests/ -v`
- [x] 18.2 Run ruff check and format: `uv run ruff check tests/` and `uv run ruff format tests/`
- [x] 18.3 Run ty check: `uv run ty check tests/`
