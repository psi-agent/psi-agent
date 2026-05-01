## Why

The psi-session component lacks comprehensive documentation, making it difficult for developers to understand its architecture, design decisions, and implementation patterns. As the core component that orchestrates the agent's conversation flow, tool execution, and workspace management, it requires clear documentation to ensure maintainability and enable future contributors to work effectively with the codebase.

## What Changes

- Add `src/psi_agent/session/CLAUDE.md` documenting:
  - Component architecture and responsibilities
  - Core data structures and types
  - Message processing flow (streaming and non-streaming)
  - Tool loading, registration, and execution patterns
  - Workspace hot-reload mechanism
  - Schedule system design
  - History persistence approach
  - Integration with psi-ai and psi-channel components

## Capabilities

### New Capabilities

- `session-documentation`: Documentation for the psi-session component, covering architecture, data flow, and implementation patterns

### Modified Capabilities

None - this is documentation only, no spec-level behavior changes.

## Impact

- `src/psi_agent/session/CLAUDE.md` (new file)
- No code changes required
