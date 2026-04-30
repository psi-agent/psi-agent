## Tasks

- [ ] Implement content tracking in `_handle_message_streaming`
  - Add `last_sent_content` variable to track last edited content
  - Modify `flush_buffer` to check content before editing
  - Modify final edit logic to check content before editing
  - Update `last_sent_content` after successful edits

- [ ] Add unit tests for content tracking
  - Test that edit is skipped when content is unchanged
  - Test that edit proceeds when content changes
  - Test that `last_sent_content` is updated correctly

- [ ] Run quality checks
  - Run `uv run ruff check`
  - Run `uv run ruff format`
  - Run `uv run ty check`
  - Run `uv run pytest` to ensure all tests pass

- [ ] Create PR and verify CI/codecov results