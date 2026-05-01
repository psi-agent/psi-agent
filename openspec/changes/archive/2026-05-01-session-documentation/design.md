## Context

psi-session is the core orchestrator component of psi-agent. It sits between psi-channel (message input) and psi-ai (LLM provider), managing the agent's conversation loop, tool execution, workspace hot-reload, and scheduled tasks.

The component has grown to include multiple subsystems:
- HTTP server for channel communication
- Message processing with tool call handling
- Dynamic tool loading from workspace
- Workspace file watching for hot-reload
- Schedule-based task execution
- History persistence

Currently there is no comprehensive documentation, making it difficult for future developers (or AI assistants) to understand the architecture without reading all source files.

## Goals / Non-Goals

**Goals:**
- Document the overall architecture and component responsibilities
- Explain the message processing flow for both streaming and non-streaming modes
- Document the tool system (loading, registration, execution)
- Document the workspace hot-reload mechanism
- Document the schedule system
- Provide clear interface definitions for each module

**Non-Goals:**
- Changing any implementation code
- Adding new features
- Modifying existing behavior

## Decisions

### Document Structure

The CLAUDE.md will follow the same structure as the AI module documentation:
- Architecture overview with component diagram
- Module structure and file responsibilities
- Core data structures (types.py)
- Key subsystems with detailed explanations
- Interface definitions (request/response formats)
- Integration points with other components

### Level of Detail

The documentation should be comprehensive enough that:
- A developer can understand the flow without reading source code
- Future AI assistants can make informed decisions about modifications
- The design rationale behind key decisions is preserved

Key areas requiring detailed documentation:
1. **Message Processing Flow**: How user messages flow through the system, including tool call loops
2. **Tool System**: How tools are discovered, loaded, registered, and executed
3. **Workspace Watcher**: The hot-reload mechanism and change detection
4. **Schedule System**: How cron-based tasks are loaded and executed
5. **Streaming vs Non-Streaming**: The differences in handling between these modes

### Interface Documentation

All external interfaces must be documented:
- HTTP API: POST /v1/chat/completions (request/response format)
- Tool function signature: `async def tool(...) -> ...`
- System module interface: `build_system_prompt()`, `compact_history()`
- Schedule file format: TASK.md with YAML frontmatter

## Risks / Trade-offs

**Documentation accuracy**: Documentation may become outdated as code changes.
→ Mitigation: Keep documentation close to code (CLAUDE.md in the same directory), review during PRs.

**Over-documentation**: Too much detail may make the document hard to navigate.
→ Mitigation: Use clear section headers, tables for structured data, and code examples for key patterns.
