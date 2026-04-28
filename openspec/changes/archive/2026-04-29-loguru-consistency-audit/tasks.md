## 1. psi-ai-anthropic-messages logging

- [x] 1.1 Add DEBUG log for full request body in `client.py:messages()` (currently only logs summary)
- [x] 1.2 Add DEBUG log for response body in `client.py:_non_stream_request()`
- [x] 1.3 Add DEBUG log for each streaming chunk in `client.py:_stream_request()`
- [x] 1.4 Add DEBUG log for request body in `server.py:_handle_chat_completions()`
- [x] 1.5 Add DEBUG log for response body in `server.py:_handle_non_streaming()`

## 2. psi-ai-openai-completions logging

- [x] 2.1 Add DEBUG log for full request body in `client.py:chat_completions()` (currently only logs summary)
- [x] 2.2 Add DEBUG log for response body in `client.py:_non_stream_request()`
- [x] 2.3 Add DEBUG log for each streaming chunk in `client.py:_stream_request()`
- [x] 2.4 Add DEBUG log for request body in `server.py:_handle_chat_completions()`
- [x] 2.5 Add DEBUG log for response body in `server.py:_handle_non_streaming()`

## 3. psi-session logging

- [x] 3.1 Add DEBUG log for AI request body in `runner.py:_run_conversation()`
- [x] 3.2 Add DEBUG log for AI response body in `runner.py:_run_conversation()`
- [x] 3.3 Add DEBUG log for tool execution result in `tool_executor.py:execute_tool()`
- [x] 3.4 Add DEBUG log for request body in `server.py:_handle_chat_completions()`
- [x] 3.5 Add DEBUG log for response body in `server.py:_handle_non_streaming()`
- [x] 3.6 Add DEBUG log for schedule content in `schedule.py:_execute_task()`
- [x] 3.7 Add DEBUG log for streaming response chunks in `runner.py:_run_streaming_conversation()`

## 4. psi-channel-cli logging

- [x] 4.1 Add DEBUG log for request body in `cli.py:send_message()`
- [x] 4.2 Add DEBUG log for response body in `cli.py:send_message()`

## 5. psi-channel-repl logging

- [x] 5.1 Add DEBUG log for request body in `client.py:send_message()`
- [x] 5.2 Add DEBUG log for response body in `client.py:send_message()`

## 6. psi-channel-telegram logging

- [x] 6.1 Add DEBUG log for request body in `client.py:send_message()`
- [x] 6.2 Add DEBUG log for response body in `client.py:send_message()`

## 7. psi-workspace-pack logging

- [x] 7.1 Add DEBUG log for mksquashfs command output in `api.py:_create_squashfs()`
- [x] 7.2 Add DEBUG log for files being copied in `api.py:_copy_directory()`

## 8. psi-workspace-mount logging

- [x] 8.1 Add DEBUG log for mount command output in `api.py:_mount_squashfs()`
- [x] 8.2 Add DEBUG log for overlayfs mount command output in `api.py:_mount_overlayfs()`

## 9. psi-workspace-snapshot logging

- [x] 9.1 Add DEBUG log for unsquashfs command output in `api.py:_extract_squashfs()`
- [x] 9.2 Add DEBUG log for mksquashfs command output in `api.py:_create_squashfs()`

## 10. psi-workspace-umount logging

- [x] 10.1 Add DEBUG log for umount command output in `api.py:_unmount()`

## 11. psi-workspace-unpack logging

- [x] 11.1 Add DEBUG log for unsquashfs command output in `api.py:unpack()`

## 12. Verification

- [x] 12.1 Run `ruff check` to ensure code quality
- [x] 12.2 Run `ruff format` to ensure formatting
- [x] 12.3 Run `ty check` to ensure type checking passes
- [x] 12.4 Run `pytest` to ensure all tests pass
