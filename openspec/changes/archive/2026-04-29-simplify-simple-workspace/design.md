## Context

The `a-simple-bash-only-workspace` is intended to be a minimal example that demonstrates the basic workspace structure. It should be easy to understand and serve as a starting point for users new to psi-agent.

The recent addition of tool result pairing repair (PR #50) added ~130 lines of complex code that is unnecessary for a simple workspace. The simple workspace doesn't need:
- Token estimation
- Tool result pairing repair
- Complex compaction logic

## Goals / Non-Goals

**Goals:**
- Reduce `a-simple-bash-only-workspace/systems/system.py` to ~50 lines
- Keep only essential functionality: skill scanning and basic truncation
- Make the code easy to read and understand for newcomers

**Non-Goals:**
- Changing `an-openclaw-like-workspace` (it should remain feature-complete)
- Adding new features
- Changing the `System` class interface

## Decisions

### Decision 1: Compaction Strategy

**Chosen approach**: Keep most recent 20 messages, discard the rest

This is the simplest possible compaction strategy:
- No token counting
- No summarization
- No repair logic
- Just slice the last 20 messages

**Alternatives considered**:
- Keep by token count: More complex, requires token estimation
- Keep by turns: More complex, requires turn detection

### Decision 2: System Prompt

**Chosen approach**: Just concatenate skill descriptions with a basic template

The system prompt should:
- State the workspace directory
- List available skills (just names and descriptions)
- Include minimal guidelines

**Alternatives considered**:
- Include tool result repair guidance: Not needed for simple workspace
- Include identifier preservation: Not needed for simple workspace

## Risks / Trade-offs

**Risk: Simple workspace may hit context limits faster**
→ Mitigation: This is acceptable - it's meant to be simple, not production-ready

**Risk: Users might copy simple workspace for production use**
→ Mitigation: Documentation should clarify this is a minimal example; use `an-openclaw-like-workspace` for production
