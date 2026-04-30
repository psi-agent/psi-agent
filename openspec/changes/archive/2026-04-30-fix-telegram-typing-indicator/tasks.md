# Tasks: Fix Telegram Typing Indicator

## Implementation Tasks

- [x] **Task 1**: Add typing indicator constant
  - Add `TYPING_INTERVAL = 4` constant in `bot.py`
  - Location: After `TELEGRAM_MAX_MESSAGE_LENGTH` constant

- [x] **Task 2**: Implement `_send_typing_periodically` helper function
  - Create async function in `TelegramBot` class
  - Send typing action in a loop with sleep interval
  - Handle errors gracefully with DEBUG logging
  - Run until cancelled

- [x] **Task 3**: Integrate typing task in `_handle_message_streaming`
  - Create typing task after initial typing action
  - Store task reference for cleanup
  - Cancel and await task in finally block or after streaming

- [x] **Task 4**: Add unit tests for typing indicator
  - Test typing task starts with streaming
  - Test typing task sends multiple indicators during long streaming
  - Test typing task is cancelled when streaming ends
  - Test typing task handles errors gracefully
  - Test typing task cleanup on exception

- [x] **Task 5**: Run quality checks
  - `uv run ruff check`
  - `uv run ruff format`
  - `uv run ty check`
  - `uv run pytest tests/channel/telegram/test_bot_streaming.py -v`

## Verification

1. Manual verification: Run the bot and observe typing indicator during streaming
2. Unit tests pass
3. All quality checks pass

## Dependencies

None - this is a self-contained fix.
