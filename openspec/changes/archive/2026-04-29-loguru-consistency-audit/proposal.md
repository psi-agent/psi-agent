## Why

The codebase lacks consistent loguru logging granularity across components. DEBUG-level logs are insufficient for tracing inter-component communication (inputs/outputs), and INFO-level logs vary in detail across different modules. This makes debugging difficult and reduces observability of the agent framework's behavior.

## What Changes

- Standardize DEBUG-level logging to include all inter-component and external API interactions with full input/output details
- Ensure INFO-level logging consistency across all modules (startup, shutdown, key operations)
- Add missing DEBUG logs for:
  - HTTP request/response bodies in all client-server communications
  - Tool execution arguments and results
  - Schedule execution details
  - Workspace watcher change detection details
  - File I/O operations in workspace components
- Establish logging guidelines for future development

## Capabilities

### New Capabilities

- `logging-standards`: Defines consistent logging granularity requirements for DEBUG and INFO levels across all psi-agent components

### Modified Capabilities

- None (this is a code quality improvement, not a behavior change)

## Impact

- All Python files in `src/psi_agent/` will be reviewed and updated
- No API or behavior changes - only logging additions/modifications
- Improves debuggability without affecting production performance (DEBUG logs are opt-in)
