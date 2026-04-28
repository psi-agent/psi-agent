## Context

The systems/ directory documentation in CLAUDE.md was left incomplete with a "具体接口待定" (interface pending) placeholder. The actual implementation was completed in commit bc5f484507fd0350d9a4853bc5ab4229ffaa31b0, which added:

1. A complete `build_system_prompt()` async function that scans skills/ directory
2. A `compact_history()` async function framework for LLM-based history compression
3. An example implementation in `examples/a-simple-bash-only-workspace/systems/system.py`

The documentation needs to be updated to reflect these actual interfaces.

## Goals / Non-Goals

**Goals:**
- Update CLAUDE.md with the complete systems/ directory specification
- Document the async interface signatures and their behavior
- Provide code examples matching the actual implementation patterns
- Maintain consistency with existing documentation style

**Non-Goals:**
- Changing the actual implementation code
- Adding new features to the systems/ interface
- Modifying the existing workspace-systems spec

## Decisions

### Decision 1: Document actual implementation from bc5f484

**Rationale:** The commit bc5f484507fd0350d9a4853bc5ab4229ffaa31b0 contains a working implementation that should be documented as-is. This provides developers with accurate reference material.

**Alternatives considered:**
- Creating new theoretical interfaces - rejected because implementation already exists
- Waiting for further changes - rejected because current implementation is complete

### Decision 2: Include code examples from the example workspace

**Rationale:** The `examples/a-simple-bash-only-workspace/systems/system.py` provides a concrete reference implementation that developers can copy and adapt.

## Risks / Trade-offs

- **Documentation drift**: Future changes to system.py may not be reflected in CLAUDE.md → Mitigation: Keep examples minimal and focus on interface contracts
