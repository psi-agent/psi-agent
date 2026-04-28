## Context

psi-agent is a componentized agent framework with four types of components (psi-ai-*, psi-session, psi-channel-*, psi-workspace-*) that communicate via Unix sockets. The codebase uses loguru for logging, but logging practices are inconsistent across modules.

### Current State Analysis

After auditing all 55 Python files in `src/psi_agent/`, the following inconsistencies were identified:

**DEBUG-level logging gaps:**

| Component | File | Missing DEBUG Logs |
|-----------|------|-------------------|
| psi-ai-anthropic | client.py | Request body (only summary), response body not logged |
| psi-ai-openai | client.py | Request body (only summary), response body not logged |
| psi-session | runner.py | AI request body not logged, tool execution results not logged |
| psi-session | server.py | Request body details not logged |
| psi-session | tool_executor.py | Tool execution result not logged |
| psi-session | schedule.py | Schedule execution details minimal |
| psi-channel-cli | cli.py | Request body not logged |
| psi-channel-repl | client.py | Request body not logged |
| psi-channel-telegram | client.py | Request body not logged |
| workspace-* | all api.py | Command outputs not logged |

**INFO-level inconsistencies:**

| Component | Current INFO | Should Be INFO |
|-----------|--------------|----------------|
| psi-ai-* | Request sent, response received | ✓ Consistent |
| psi-session | Tool loaded, schedule executed | ✓ Mostly consistent |
| psi-channel-* | Message received/sent | ✓ Consistent |
| workspace-* | Operation started/completed | ✓ Consistent |

**Good patterns observed:**

- `psi-ai-*/client.py`: Logs request summary with message count
- `psi-ai-*/server.py`: Logs route configuration
- `psi-session/runner.py`: Logs tool count on startup
- `psi-session/workspace_watcher.py`: Logs detected changes

## Goals / Non-Goals

**Goals:**

1. Establish consistent DEBUG-level logging for all inter-component and external API communications
2. Ensure every HTTP request/response is logged with full details at DEBUG level
3. Log tool execution arguments and results at DEBUG level
4. Standardize INFO-level logging for key lifecycle events

**Non-Goals:**

1. Changing log format or structure
2. Adding new log levels
3. Modifying production behavior (DEBUG is opt-in)
4. Adding logging to pure utility functions or data classes

## Decisions

### Decision 1: DEBUG-level logging scope

**Chosen:** Log all inputs and outputs for:
- HTTP requests (URL, headers, body)
- HTTP responses (status, body)
- Tool calls (name, arguments, result)
- Schedule executions (name, content)
- File I/O operations (path, action)

**Rationale:** These are the boundaries where things go wrong. Internal logic is less critical.

**Alternatives considered:**
- Log everything: Too verbose, would obscure important information
- Log only errors: Insufficient for debugging

### Decision 2: INFO-level logging standardization

**Chosen:** INFO logs should cover:
- Component startup/shutdown
- Request received/sent (without body details)
- Tool/schedule execution (name only)
- Configuration loaded
- Errors with context

**Rationale:** INFO should give a high-level view of system activity without overwhelming detail.

### Decision 3: Sensitive data handling

**Chosen:** Mask sensitive values (API keys, tokens) in logs, but log structure.

**Rationale:** Security requirement - credentials must never appear in logs.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Verbose DEBUG logs may impact performance | DEBUG is opt-in; production uses INFO/WARNING |
| Log volume may be large | Acceptable for debugging; users control log level |
| Sensitive data exposure | Mask all credentials before logging |
