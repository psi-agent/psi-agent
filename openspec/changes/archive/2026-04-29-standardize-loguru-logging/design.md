## Context

psi-agent is a componentized agent framework with four component types (psi-ai-*, psi-session, psi-channel-*, psi-workspace-*). Components communicate via HTTP over Unix sockets. The codebase uses loguru for logging but lacks consistent granularity standards.

Current state analysis reveals:
- **Good DEBUG coverage**: AI clients (anthropic_messages/client.py, openai_completions/client.py) have detailed request/response logging
- **Inconsistent INFO coverage**: Some components log every request (session/server.py), others only log startup
- **Missing DEBUG logs**: Several areas lack detailed input/output logging:
  - channel/cli/cli.py: Missing request body logging
  - session/tool_executor.py: Only logs tool name, not full arguments
  - session/schedule.py: Missing execution content details
  - workspace components: Missing command execution details

## Goals / Non-Goals

**Goals:**
- Establish clear logging granularity standards for DEBUG and INFO levels
- Ensure all inter-component communication has DEBUG-level input/output logging
- Ensure INFO-level logging has consistent granularity across components
- Document logging standards in CLAUDE.md for future development

**Non-Goals:**
- Add new log levels (WARNING, ERROR) - these are already consistent
- Change existing log message formats
- Add structured logging or log aggregation
- Performance optimization for logging

## Decisions

### Decision 1: DEBUG-Level Logging Standard

**Decision**: DEBUG level shall log all inter-component communication inputs and outputs.

**Rationale**: DEBUG level is for development/troubleshooting. Full visibility into request/response bodies, tool arguments/results, and schedule execution details is essential for debugging distributed agent behavior.

**Standard**:
- HTTP requests: Log full request body (JSON) at DEBUG
- HTTP responses: Log full response body (JSON) at DEBUG
- Tool calls: Log tool name, arguments, and result at DEBUG
- Schedule execution: Log schedule name, content, and timing at DEBUG
- Workspace changes: Log detected changes with details at DEBUG
- Command execution: Log full command and output at DEBUG

**Sensitive data**: Always mask API keys, tokens, passwords in DEBUG logs.

### Decision 2: INFO-Level Logging Standard

**Decision**: INFO level shall log significant lifecycle events and operation summaries.

**Rationale**: INFO level is for production monitoring. It should provide a clear operational picture without overwhelming detail.

**Standard**:
- Component startup/shutdown: Log component name and key configuration
- Request received: Log request type and summary (not full body)
- Response sent: Log response status and summary
- Tool loaded/updated: Log tool name
- Schedule started/completed: Log schedule name
- Workspace changes detected: Log change summary
- Errors: Log error type and message (full details at DEBUG/ERROR)

### Decision 3: Log Message Format

**Decision**: Use consistent, concise log message formats.

**Format patterns**:
- Startup: `"Starting {component_name}"`
- Shutdown: `"{component_name} stopped"`
- Request received: `"Received POST {path} request"`
- Request sent: `"Sending request to {url}"`
- Response: `"Returning successful {streaming|non-streaming} response"`
- Tool execution: `"Executing tool: {tool_name} with arguments: {args}"`
- Tool result: `"Tool result: {result}"` (truncated if too long)

## Risks / Trade-offs

**Risk: Log volume increase**
→ Mitigation: DEBUG is opt-in via log level configuration. Production deployments typically use INFO or WARNING.

**Risk: Sensitive data exposure**
→ Mitigation: Already implemented via `mask_sensitive_args()` for CLI arguments. Ensure API keys/tokens are masked in all DEBUG logs.

**Risk: Performance impact from JSON serialization**
→ Mitigation: Only serialize at DEBUG level. Use `logger.debug()` which is a no-op when DEBUG is disabled.
