## 1. Refactor streaming parsing in runner.py

- [x] 1.1 Extract `_parse_streaming_response` helper method
- [x] 1.2 Update `_run_conversation` to use helper
- [x] 1.3 Update `_stream_conversation` to use helper
- [x] 1.4 Add DEBUG log for request body in `_stream_conversation`

## 2. Add DEBUG logs to server.py

- [x] 2.1 Add DEBUG log for streaming response completion in `_handle_streaming`

## 3. Add DEBUG logs to tool_loader.py

- [x] 3.1 Add DEBUG log for tools being loaded in `load_all_tools`

## 4. Add DEBUG logs to schedule.py

- [x] 4.1 Add DEBUG log for successful schedule load in `load_schedule`