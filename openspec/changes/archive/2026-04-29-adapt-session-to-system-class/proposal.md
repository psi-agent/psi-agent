## Why

The `systems/system.py` interface has been refactored from module-level functions to a `System` class. The psi-session currently calls `module.build_system_prompt()` directly and doesn't use `compact_history()` at all. This change adapts psi-session to instantiate the `System` class and use its methods, enabling stateful operations like incremental summary updates.

## What Changes

- **BREAKING**: psi-session now expects `systems/system.py` to export a `System` class, not module-level functions
- Session runner instantiates `System` object on startup and stores it for the session lifetime
- Session runner calls `system.build_system_prompt()` as an instance method
- Session runner integrates `system.compact_history()` into the conversation loop for history management
- Session runner provides a `complete_fn` to `compact_history()` for LLM-based summarization

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `session-core`: Session now instantiates `System` class and uses instance methods for system prompt and history compaction

## Impact

- `src/psi_agent/session/runner.py` - Main changes to instantiate and use `System` class
- `openspec/specs/session-core/spec.md` - Update requirements to reflect `System` class usage
- All workspaces using `systems/system.py` must be updated to use `System` class (already done for example workspaces)
