## ADDED Requirements

### Requirement: Telegram channel provides CLI entry point

The Telegram channel SHALL provide a CLI command `psi-channel-telegram` for starting the bot.

#### Scenario: CLI starts with token argument
- **WHEN** `psi-channel-telegram --token <token> --session-socket <path>` is invoked
- **THEN** the bot SHALL initialize and connect to the session

#### Scenario: Missing token shows error
- **WHEN** `psi-channel-telegram` is invoked without `--token`
- **THEN** the CLI SHALL display an error and exit

### Requirement: Telegram channel receives messages via polling

The Telegram channel SHALL use long polling to receive updates from Telegram Bot API.

#### Scenario: Receive text message
- **WHEN** a user sends a text message to the bot
- **THEN** the channel SHALL receive the message via polling

#### Scenario: Polling starts on bot initialization
- **WHEN** the bot starts
- **THEN** polling SHALL begin automatically using `python-telegram-bot`'s `Application.run_polling()`

### Requirement: Telegram channel is a pure message forwarder

The Telegram channel SHALL NOT process any commands. It only forwards messages between Telegram and psi-session.

#### Scenario: Ignore /start command
- **WHEN** a user sends `/start` command (Telegram bot initialization)
- **THEN** the channel SHALL ignore the message and not forward it to session

#### Scenario: Forward all messages as-is
- **WHEN** a user sends any message that is not `/start`
- **THEN** the channel SHALL forward the message content unchanged to session
- **AND** session is responsible for handling skills and tools

### Requirement: Telegram channel forwards messages to session

The Telegram channel SHALL forward user messages to psi-session via Unix socket using async HTTP.

#### Scenario: Forward user message
- **WHEN** a text message is received from a Telegram user
- **THEN** the channel SHALL send the message to psi-session via HTTP POST to `/v1/chat/completions`
- **AND** the HTTP client SHALL use `aiohttp` with async API

#### Scenario: Include user identifier
- **WHEN** forwarding a message to session
- **THEN** the request SHALL include a user identifier in format `telegram:<user_id>`

### Requirement: Telegram channel sends responses to users

The Telegram channel SHALL send session responses back to the Telegram user.

#### Scenario: Send text response
- **WHEN** session returns a text response
- **THEN** the channel SHALL send the response as a text message to the originating Telegram user

#### Scenario: Handle long responses
- **WHEN** session returns a response longer than Telegram's 4096 character limit
- **THEN** the channel SHALL split the response into multiple messages

### Requirement: Telegram channel handles errors gracefully

The Telegram channel SHALL handle errors without crashing.

#### Scenario: Session connection failure
- **WHEN** the session socket is unavailable
- **THEN** the channel SHALL log the error and send an error message to the user

#### Scenario: Telegram API error
- **WHEN** Telegram API returns an error
- **THEN** the channel SHALL log the error and continue running

### Requirement: Telegram channel supports graceful shutdown

The Telegram channel SHALL support graceful shutdown on SIGINT/SIGTERM.

#### Scenario: Shutdown on Ctrl+C
- **WHEN** SIGINT is received
- **THEN** the channel SHALL stop polling, close connections, and exit cleanly

### Requirement: Telegram channel uses async architecture

The Telegram channel SHALL use async/await for ALL I/O operations without exception.

#### Scenario: Async message handling
- **WHEN** multiple messages arrive concurrently
- **THEN** the channel SHALL handle them asynchronously without blocking

#### Scenario: Async session communication
- **WHEN** communicating with session via Unix socket
- **THEN** the channel SHALL use `aiohttp.UnixConnector` with async API

#### Scenario: Async Telegram polling
- **WHEN** polling for Telegram updates
- **THEN** the channel SHALL use `python-telegram-bot` v20+ async API

#### Scenario: No blocking I/O
- **WHEN** any I/O operation is performed
- **THEN** it SHALL use async methods (aiohttp, anyio, asyncio)
- **AND** synchronous I/O (requests, subprocess.run, open) is prohibited
