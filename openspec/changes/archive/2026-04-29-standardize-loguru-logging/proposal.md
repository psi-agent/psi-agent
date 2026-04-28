## Why

The codebase lacks consistent loguru logging granularity across components. Some files have detailed DEBUG-level logging for inter-component communication while others are missing critical input/output logging. INFO-level logging varies significantly in detail—some components log every request/response while others only log startup/shutdown. This inconsistency makes debugging difficult and reduces observability of the agent framework's behavior.

## What Changes

- **Standardize DEBUG-level logging**: Ensure all inter-component communication (HTTP requests/responses over Unix sockets, tool calls, schedule execution) includes input/output logging at DEBUG level
- **Standardize INFO-level logging**: Ensure consistent granularity across all components for normal operations (startup, shutdown, request received, response sent, tool loaded, schedule executed)
- **Add missing DEBUG logs**: Identify and add missing DEBUG logs for:
  - Request body/response body in all HTTP handlers and clients
  - Tool execution arguments and results
  - Schedule execution details
  - Workspace watcher change detection details
- **Ensure sensitive data masking**: Verify all sensitive data (API keys, tokens) are masked in logs

## Capabilities

### New Capabilities

- `logging-granularity`: Defines the logging granularity standards for DEBUG and INFO levels across all psi-agent components

### Modified Capabilities

None - this is a new capability that standardizes existing logging practices.

## Impact

- **Affected files**: All Python files in `src/psi_agent/` that use loguru
- **Components affected**:
  - `psi-ai-anthropic-messages`: client.py, server.py
  - `psi-ai-openai-completions`: client.py, server.py
  - `psi-channel-cli`: cli.py
  - `psi-channel-repl`: client.py, repl.py
  - `psi-channel-telegram`: client.py, bot.py
  - `psi-session`: runner.py, server.py, tool_executor.py, tool_loader.py, schedule.py, workspace_watcher.py, history.py
  - `psi-workspace-*`: mount/api.py, pack/api.py, snapshot/api.py, umount/api.py, unpack/api.py, manifest.py
  - `utils`: proctitle.py
- **No API changes**: Logging changes are internal and do not affect public APIs
- **No breaking changes**: Only adding/modifying log statements
