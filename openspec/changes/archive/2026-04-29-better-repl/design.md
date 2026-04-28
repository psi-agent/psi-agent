## Context

The current REPL implementation in `psi-channel-repl` uses `sys.stdin.readline()` wrapped in `run_in_executor()` for async compatibility. This approach has significant limitations:

- No input history navigation (up/down arrows don't work)
- No line editing (left/right arrows, backspace behavior varies)
- No multi-line input support
- Poor terminal integration across different environments
- Uses executor threads which adds overhead

`prompt-toolkit` is a mature library designed specifically for building interactive CLI applications with excellent async support.

## Goals / Non-Goals

**Goals:**
- Replace stdin reading with `prompt-toolkit`'s async `PromptSession`
- Enable input history navigation with up/down arrows
- Enable full line editing (cursor movement, text manipulation)
- Support multi-line input with proper handling
- Maintain backward compatibility with existing REPL behavior and API
- Use native async API without executor threads

**Non-Goals:**
- Syntax highlighting (not needed for plain text input)
- Auto-completion (no context for suggestions)
- Custom keybindings beyond defaults
- Saving/loading history to disk (can be added later)

## Decisions

### Decision: Use `prompt-toolkit` with `PromptSession`

**Rationale:** `PromptSession` provides:
- Built-in history with arrow key navigation
- Full line editing out of the box
- Native async support via `prompt_async()`
- Cross-platform terminal handling

**Alternatives considered:**
- `readline` module: Not async-friendly, requires executor threads
- `click` + manual editing: Reinventing the wheel
- Keep current approach: Doesn't meet user experience goals

### Decision: Store history in `InMemoryHistory`

**Rationale:** `prompt-toolkit` provides `InMemoryHistory` which stores session history. This matches the current behavior where history is not persisted across sessions.

**Future extension:** Can easily switch to `FileHistory` if persistent history is desired.

### Decision: Use simple prompt string without formatting

**Rationale:** Keep the prompt minimal (`"> "`) to match the current behavior. Can be enhanced later with colors/formatting if needed.

### Decision: Handle multi-line via Enter key

**Rationale:** For a chat interface, single Enter should submit. Multi-line can be added later via a meta-enter binding if needed. This matches current behavior where Enter submits immediately.

## Risks / Trade-offs

- **Risk: New dependency** → Add `prompt-toolkit` to project dependencies. It's a mature, well-maintained library.
- **Risk: Terminal compatibility** → `prompt-toolkit` handles cross-platform differences internally. Falls back gracefully on limited terminals.
- **Risk: Learning curve** → API is straightforward. Documentation is excellent.
