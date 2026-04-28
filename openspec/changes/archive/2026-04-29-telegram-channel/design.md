## Context

psi-agent uses a component-based architecture where channels handle platform-specific communication. The existing REPL channel (`psi-channel-repl`) demonstrates the pattern: it connects to psi-session via Unix socket using HTTP with OpenAI chat completion format.

Telegram channel will follow the same pattern but receive messages from Telegram's Bot API via webhooks or polling, then forward them to psi-session.

**Current Architecture:**
- Channel connects to session via Unix socket (`aiohttp.UnixConnector`)
- Uses OpenAI chat completion format for messages
- Session handles conversation history and tool calling
- Channel only sends/receives final messages

## Goals / Non-Goals

**Goals:**
- Implement `psi-channel-telegram` CLI with `--token` argument
- Use `python-telegram-bot` (v20+) with async support
- Support multiple concurrent Telegram users
- Handle text messages bidirectionally
- Follow existing channel patterns (config, client, CLI structure)

**Non-Goals:**
- No message processing in channel - all skills and tools handled by session
- No support for media messages (images, files, voice) in initial version
- No inline query handling
- No Telegram payment or game features
- No message editing/deletion tracking
- No group chat support (private chats only for v1)

## Decisions

### 1. Use `python-telegram-bot` library (v20+)

**Rationale:** Most popular Python Telegram library with native async support (v20+). Well-maintained, extensive documentation, and handles webhook/polling abstraction.

**Alternatives considered:**
- `aiogram`: Also good async support, but `python-telegram-bot` has larger community
- Raw HTTP API: More control but reinvents the wheel

### 2. Use polling (getUpdates) instead of webhooks

**Rationale:** Simpler deployment - no need for public HTTPS endpoint or SSL certificates. Polling is sufficient for low-to-medium traffic bots.

**Alternatives considered:**
- Webhooks: More efficient for high traffic, requires public URL and HTTPS
- Hybrid: Start with polling, add webhook support later if needed

### 3. User identification via Telegram user ID

**Rationale:** Each Telegram user has a unique numeric ID. We'll use this to identify users when communicating with session. Session can use this for conversation isolation.

**Format:** `telegram:<user_id>` as user identifier

### 4. Message format: Plain text only

**Rationale:** Telegram supports Markdown/HTML formatting, but psi-session returns plain text. We'll send plain text and let Telegram handle display.

### 5. Channel is a pure forwarder

**Rationale:** Channel is strictly an interface layer. It does not interpret or process any message content. Only `/start` is ignored (Telegram bot initialization message). All other messages are forwarded unchanged to session, which handles skills and tools.

**What channel does NOT do:**
- Interpret or process message content
- Handle skills or tools
- Maintain conversation state

### 6. Module structure mirrors REPL channel

```
src/psi_agent/channel/telegram/
├── __init__.py
├── cli.py        # tyro CLI entry point
├── config.py     # TelegramConfig dataclass
├── client.py     # Session client (reuse pattern from REPL)
└── bot.py        # Telegram bot handler
```

### 7. All I/O must use async methods

**Rationale:** psi-agent core architecture requirement. All I/O operations must use async interfaces to avoid blocking the event loop.

**Required async libraries:**
- HTTP client: `aiohttp` (not `requests`)
- File I/O: `anyio.open_file()` (not `open()`)
- Subprocess: `asyncio.create_subprocess_exec` (not `subprocess.run`)
- Telegram: `python-telegram-bot` v20+ async API

## Risks / Trade-offs

**Risk: Rate limiting by Telegram API**
→ Mitigation: `python-telegram-bot` handles rate limiting internally. For high traffic, consider webhook mode.

**Risk: Long polling blocks shutdown**
→ Mitigation: Use `Application.stop()` properly in signal handler. Test graceful shutdown.

**Risk: No message persistence - lost messages during downtime**
→ Mitigation: Accept for v1. Future: add message queue or webhook with persistent storage.

**Trade-off: Polling vs Webhooks**
→ Polling is simpler but less efficient. Can migrate to webhooks later without API changes.
