## Why

When a user passes a relative workspace path to psi-session, the system may look up skills/tools/schedules from the wrong directory (cwd instead of the specified workspace). This causes inconsistent behavior and breaks workspace portability - a core design goal of psi-agent.

## What Changes

- The workspace path will be resolved to an absolute path at session initialization
- All workspace subdirectory paths (tools/, skills/, schedules/, systems/) will be consistently derived from the resolved absolute path
- The System class in workspace systems/system.py will receive an absolute path

## Capabilities

### New Capabilities

- `workspace-path-resolution`: Workspace paths SHALL be resolved to absolute paths at session initialization to ensure consistent file access regardless of current working directory.

### Modified Capabilities

- `session-core`: The session SHALL resolve the workspace path to an absolute path before passing it to the System class and workspace watcher.
- `workspace-hot-reload`: The workspace watcher SHALL use the resolved absolute workspace path for detecting file changes.

## Impact

- `src/psi_agent/session/config.py`: Add path resolution in `workspace_path()` method
- `src/psi_agent/session/runner.py`: Ensure workspace path is resolved before use
- Tests for path resolution with relative paths
