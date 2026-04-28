## 1. Setup

- [x] 1.1 Add `python-telegram-bot` dependency to pyproject.toml
- [x] 1.2 Create `src/psi_agent/channel/telegram/__init__.py` module
- [x] 1.3 Create `src/psi_agent/channel/telegram/config.py` with TelegramConfig dataclass

## 2. Core Implementation

- [x] 2.1 Create `src/psi_agent/channel/telegram/client.py` for session communication (reuse pattern from REPL)
- [x] 2.2 Create `src/psi_agent/channel/telegram/bot.py` with message handler
- [x] 2.3 Implement message forwarding from Telegram to session
- [x] 2.4 Implement response sending from session to Telegram
- [x] 2.5 Add message splitting for responses > 4096 characters

## 3. CLI Entry Point

- [x] 3.1 Create `src/psi_agent/channel/telegram/cli.py` with tyro CLI
- [x] 3.2 Add `psi-channel-telegram` entry point to pyproject.toml
- [x] 3.3 Update `src/psi_agent/channel/cli.py` to include telegram subcommand

## 4. Error Handling & Shutdown

- [x] 4.1 Add error handling for session connection failures
- [x] 4.2 Add error handling for Telegram API errors
- [x] 4.3 Implement graceful shutdown on SIGINT/SIGTERM

## 5. Testing

- [x] 5.1 Write unit tests for TelegramConfig
- [x] 5.2 Write unit tests for session client
- [x] 5.3 Write unit tests for message splitting logic
- [x] 5.4 Run all quality checks (format, lint, typing, test)
