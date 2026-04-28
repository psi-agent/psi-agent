## Context

psi-agent uses a component architecture where `psi-channel-*` components handle user interaction. The REPL channel will be the simplest channel implementation, providing a basic interactive interface for development and testing.

Key constraints from the architecture:
- Channel communicates with psi-session via HTTP over Unix socket
- Channel acts as client, session acts as server
- Only final messages are exchanged, tool calling is internal to session

## Goals / Non-Goals

**Goals:**
- Implement minimal REPL interface for continuous conversation
- Support conversation history for context
- Provide graceful exit mechanisms
- Keep implementation simple for development/testing use cases

**Non-Goals:**
- Advanced line editing (arrow keys, history navigation) - use readline or prompt-toolkit for that
- Rich text formatting or markdown rendering
- Multi-line input support
- Session persistence or save/load functionality

## Decisions

### Use stdlib asyncio for async I/O

**Decision**: Use `asyncio` with `asyncio.open_connection()` for async stdin/stdout.

**Rationale**:
- No external dependencies needed
- Simple and sufficient for basic REPL
- Follows project's async-first design

**Alternative considered**: `prompt-toolkit` for rich editing. Rejected because it adds complexity and dependencies for a simple development tool.

### Simple message format with session

**Decision**: Send messages to session using OpenAI chat completion format over HTTP.

**Rationale**:
- Consistent with existing psi-ai-* components
- Session expects this format
- Easy to test and debug

### Maintain conversation history in memory

**Decision**: Keep a list of messages in memory and send with each request.

**Rationale**:
- Enables context for multi-turn conversations
- Simple implementation without persistence
- Session handles history compaction if needed

## Risks / Trade-offs

- **No line editing**: Users cannot edit previous lines. Acceptable for development use.
- **Memory usage**: Long conversations consume memory. Session's `compact_history()` handles this.
- **No persistence**: Conversation lost on exit. Acceptable for REPL use case.
