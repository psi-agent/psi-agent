## 1. CLI Entrypoint Testing

- [x] 1.1 Create `tests/test_main.py` for `__main__.py` entrypoint tests
- [x] 1.2 Test main entrypoint routes to session subcommand
- [x] 1.3 Test main entrypoint routes to ai subcommand
- [x] 1.4 Test main entrypoint routes to channel subcommand
- [x] 1.5 Test main entrypoint routes to workspace subcommand
- [x] 1.6 Test CLI validates required arguments and shows error
- [x] 1.7 Test CLI handles `--help` flag correctly

## 2. Workspace Snapshot Testing

- [x] 2.1 Create `tests/workspace/test_snapshot_api.py` for snapshot API tests
- [x] 2.2 Test snapshot creates layer from mounted workspace (mock subprocess)
- [x] 2.3 Test snapshot with tag parameter updates manifest
- [x] 2.4 Test snapshot validates squashfs path exists
- [x] 2.5 Test snapshot validates mount point exists
- [x] 2.6 Test snapshot handles permission errors gracefully
- [x] 2.7 Test snapshot handles disk space errors gracefully

## 3. Workspace Mount Testing

- [x] 3.1 Create `tests/workspace/test_mount_api.py` for mount API tests
- [x] 3.2 Test mount creates overlayfs from squashfs (mock subprocess)
- [x] 3.3 Test mount specific layer by tag
- [x] 3.4 Test mount validates squashfs path exists
- [x] 3.5 Test mount validates output directory does not exist
- [x] 3.6 Test mount handles permission errors gracefully
- [x] 3.7 Test mount handles invalid squashfs format errors

## 4. Channel CLI Testing

- [x] 4.1 Create `tests/channel/test_cli.py` for channel CLI tests
- [x] 4.2 Test channel CLI routes to REPL subcommand
- [x] 4.3 Test channel CLI routes to Telegram subcommand
- [x] 4.4 Test channel CLI validates required session-socket argument
- [x] 4.5 Test Telegram channel validates required token argument
- [x] 4.6 Test channel CLI handles `--help` flag

## 5. Schedule Execution Testing

- [x] 5.1 Create `tests/session/test_schedule.py` for schedule executor tests
- [x] 5.2 Test schedule executor loads valid task from workspace
- [x] 5.3 Test schedule executor skips task with invalid cron expression
- [x] 5.4 Test schedule executor handles missing schedules directory
- [x] 5.5 Test schedule executor triggers task on schedule (time mock)
- [x] 5.6 Test schedule executor triggers multiple tasks concurrently
- [x] 5.7 Test schedule executor handles task execution errors
- [x] 5.8 Test schedule executor hot reloads modified task
- [x] 5.9 Test schedule executor registers new task file
- [x] 5.10 Test schedule executor unregisters removed task file

## 6. Additional CLI Testing

- [x] 6.1 Add tests for `ai/openai_completions/cli.py` (current 52%)
- [x] 6.2 Add tests for `ai/anthropic_messages/cli.py` (current 53%)
- [x] 6.3 Add tests for `session/cli.py` (current 52%)
- [x] 6.4 Add tests for `channel/repl/cli.py` (current 68%)
- [x] 6.5 Add tests for `channel/telegram/cli.py` (current 69%)

## 7. Verification

- [x] 7.1 Run full test suite and verify all tests pass
- [x] 7.2 Generate coverage report and verify 90%+ overall coverage
- [x] 7.3 Verify all previously low-coverage modules now have 80%+ coverage
