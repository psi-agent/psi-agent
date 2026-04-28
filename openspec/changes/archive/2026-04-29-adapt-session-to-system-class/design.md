## Context

psi-session currently uses module-level functions from `systems/system.py`:
- Calls `module.build_system_prompt()` directly
- Does not use `compact_history()` at all

The `System` class refactoring introduced:
- Instance methods instead of module-level functions
- State management (`_previous_summary` for incremental updates)
- `complete_fn` parameter for LLM-based summarization

Session needs to:
1. Instantiate `System` object on startup
2. Store the instance for the session lifetime
3. Call instance methods for system prompt and history compaction
4. Provide a `complete_fn` for summarization

## Goals / Non-Goals

**Goals:**
- Adapt psi-session to use `System` class instead of module-level functions
- Integrate history compaction into the conversation loop
- Provide `complete_fn` for LLM-based summarization
- Maintain backward compatibility with existing session behavior

**Non-Goals:**
- Modifying psi-ai-* components
- Changing the HTTP protocol between session and channel
- Implementing new compaction algorithms (already in `System` class)

## Decisions

### 1. System Instance Lifecycle

**Decision:** Instantiate `System` object in `SessionRunner.__aenter__()` and store as `self._system`.

**Rationale:**
- Session needs the instance for its entire lifetime (state management)
- `__aenter__` is the natural initialization point
- Consistent with other resource initialization (client, watcher)

### 2. System Prompt Loading

**Decision:** Replace `load_system_prompt()` function with `_load_system()` that instantiates the class.

**Rationale:**
- Old function called `module.build_system_prompt()` directly
- New approach: instantiate `System`, then call `system.build_system_prompt()`
- Simpler: one function does both instantiation and prompt generation

### 3. History Compaction Integration

**Decision:** Call `system.compact_history()` in `_build_messages()` before building the messages list.

**Rationale:**
- Compaction should happen before sending messages to LLM
- `_build_messages()` is the natural place (already builds messages)
- Pass `self._complete_fn` for LLM-based summarization

### 4. CompleteFn Implementation

**Decision:** Create `_complete_fn()` method that calls psi-ai for single-turn summarization.

**Rationale:**
- `complete_fn` signature: `Callable[[list[dict]], Awaitable[str]]`
- Session already has HTTP client to psi-ai
- Use the same OpenAI chat completion protocol
- Single request/response, no tool calls

## Risks / Trade-offs

- **Breaking change for workspaces** → All workspaces must update `system.py` (already done for examples)
- **Compaction adds latency** → Only triggered when history exceeds limit, acceptable trade-off
- **State management in session** → `_previous_summary` persists across requests, matches OpenClaw behavior