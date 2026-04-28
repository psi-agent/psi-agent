## 1. Update CLAUDE.md with logging standards

- [x] 1.1 Add logging granularity section to CLAUDE.md documenting DEBUG and INFO level standards

## 2. Fix psi-ai-anthropic-messages logging

- [x] 2.1 Add DEBUG log for translated request body summary in server.py
- [x] 2.2 Add DEBUG log for streaming event details in client.py

## 3. Fix psi-ai-openai-completions logging

- [x] 3.1 Add DEBUG log for request body summary in server.py (already has full body log)

## 4. Fix psi-channel-cli logging

- [x] 4.1 Add DEBUG log for request body in send_message function
- [x] 4.2 Add DEBUG log for response body in _handle_non_streaming function
- [x] 4.3 Add DEBUG log for streaming chunks in _handle_streaming function

## 5. Fix psi-channel-repl logging

- [x] 5.1 Add DEBUG log for request body in client.py (already present)
- [x] 5.2 Add DEBUG log for response content in client.py (already present)

## 6. Fix psi-channel-telegram logging

- [x] 6.1 Add DEBUG log for request body in client.py (already present)
- [x] 6.2 Add DEBUG log for response content in client.py (already present)

## 7. Fix psi-session logging

- [x] 7.1 Add DEBUG log for tool arguments in tool_executor.py
- [x] 7.2 Add DEBUG log for tool result in tool_executor.py (already present but needs improvement)
- [x] 7.3 Add DEBUG log for schedule execution content in schedule.py
- [x] 7.4 Add DEBUG log for schedule next run time in schedule.py (already present)
- [x] 7.5 Add DEBUG log for workspace change detection details in workspace_watcher.py (already has INFO)
- [x] 7.6 Add DEBUG log for AI request body in runner.py (already present)
- [x] 7.7 Add DEBUG log for AI response body in runner.py (already present)
- [x] 7.8 Add DEBUG log for streaming content chunks in runner.py (already present)

## 8. Fix psi-workspace-mount logging

- [x] 8.1 Add DEBUG log for mount command execution in api.py (already present)
- [x] 8.2 Add DEBUG log for overlayfs mount command in api.py (already present)
- [x] 8.3 Add DEBUG log for target layer resolution in api.py (already present)

## 9. Fix psi-workspace-pack logging

- [x] 9.1 Add DEBUG log for layer UUID and tag in api.py (already present)
- [x] 9.2 Add DEBUG log for copy operations in api.py (already present)
- [x] 9.3 Add DEBUG log for mksquashfs command in api.py (already present)

## 10. Fix psi-workspace-snapshot logging

- [x] 10.1 Add DEBUG log for snapshot creation details in api.py (already present)
- [x] 10.2 Add DEBUG log for unsquashfs command in api.py (already present)
- [x] 10.3 Add DEBUG log for mksquashfs command in api.py (already present)

## 11. Fix psi-workspace-umount logging

- [x] 11.1 Add DEBUG log for umount command in api.py (already present)
- [x] 11.2 Add DEBUG log for cleanup operations in api.py (already present)

## 12. Fix psi-workspace-unpack logging

- [x] 12.1 Add DEBUG log for unsquashfs command in api.py (already present)

## 13. Fix utils/proctitle logging

- [x] 13.1 Add DEBUG log for masked arguments in proctitle.py (already present)

## 14. Run quality checks

- [x] 14.1 Run `ruff check` on all modified files
- [x] 14.2 Run `ruff format` on all modified files
- [x] 14.3 Run `ty check` on all modified files
- [x] 14.4 Run tests to verify no regressions
