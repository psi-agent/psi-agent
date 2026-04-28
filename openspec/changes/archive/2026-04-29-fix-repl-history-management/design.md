## Context

Currently, both REPL channel and session maintain message history:

1. **REPL (`repl.py`)**: Maintains `self.history: list[dict[str, str]]`, appends user/assistant messages, sends entire history to session on each request.

2. **Session (`runner.py`)**: Maintains `self.history: History`, loads from file on startup, appends messages, persists to file.

3. **Session Server (`server.py`)**: Receives full message list from channel, extracts only the last user message, discards the rest.

This creates:
- Redundant state management
- Unnecessary data transfer (11 messages sent when only 1 is needed)
- Confusion about who owns conversation state

The architectural principle: **Session is the single source of truth for conversation state**. Channel should only handle input/output, not state.

## Goals / Non-Goals

**Goals:**
- Remove history management from REPL channel
- Channel sends only current user message to session
- Session remains sole authority on conversation history
- Maintain backward compatibility with session API

**Non-Goals:**
- Changes to session history management (already correct)
- Changes to other channels (if any)
- Adding new features

## Decisions

### Decision 1: Channel sends single message, not message list

**Rationale:** Session already extracts only the last user message from the request. Sending the full history is wasteful and semantically incorrect - channel shouldn't know about conversation history.

**API Change:**
```python
# Before
async def send_message(self, messages: list[dict[str, str]]) -> str

# After
async def send_message(self, message: str) -> str
```

### Decision 2: Remove history from REPL class

**Rationale:** The `self.history` attribute in `Repl` class serves no purpose after Decision 1. Session manages all history.

**Code Change:**
```python
# Before
class Repl:
    def __init__(self, config: ReplConfig) -> None:
        self.history: list[dict[str, str]] = []

    async def run(self) -> None:
        self.history.append({"role": "user", "content": user_input})
        response = await self.client.send_message(self.history)
        self.history.append({"role": "assistant", "content": response})

# After
class Repl:
    async def run(self) -> None:
        response = await self.client.send_message(user_input)
```

### Decision 3: Keep session API unchanged

**Rationale:** Session server already handles the request correctly - it extracts the last user message from the messages array. We can keep the request format as-is (messages array with single user message) for consistency with OpenAI API format.

**No change needed to session.**

## Risks / Trade-offs

- **Risk:** If other channels exist that rely on sending full history, they would break.
  - **Mitigation:** Check for other channel implementations. Currently only REPL exists.

- **Trade-off:** Channel loses visibility into conversation history.
  - **Acceptable:** Channel should only handle I/O, not state. This is the correct architectural boundary.
