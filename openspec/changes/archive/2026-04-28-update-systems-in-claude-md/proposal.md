## Why

The systems/ directory design was marked as "待定" (pending) in CLAUDE.md, but it has since been fully designed and implemented in commit bc5f484507fd0350d9a4853bc5ab4229ffaa31b0. The documentation needs to be updated to reflect the actual async interfaces and implementation patterns.

## What Changes

- Update the systems/ directory section in CLAUDE.md with complete interface specifications
- Document the `build_system_prompt()` async function with its skill scanning behavior
- Document the `compact_history()` async function with its LLM summarization framework
- Add code examples showing the actual implementation patterns
- Remove the "具体接口待定" placeholder note

## Capabilities

### New Capabilities

None - this is a documentation update only.

### Modified Capabilities

- `workspace-systems`: Update spec to reflect the completed async interface design (already exists from bc5f484)

## Impact

- CLAUDE.md documentation file
- Developers referencing the workspace systems/ directory structure
