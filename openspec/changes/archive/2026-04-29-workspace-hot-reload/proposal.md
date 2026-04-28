## Why

Currently, psi-session only loads workspace files (tools, skills, schedules) at startup. Changes to these files during runtime require a session restart. This creates a poor developer experience when iterating on tools, skills, or schedules during development or when dynamically updating agent capabilities in production.

The system prompt is built once at startup via `build_system_prompt()` and cached, so any changes to skills or schedules are not reflected without restarting the session.

## What Changes

- Add file change detection for workspace files on every user message
- Implement hash-based change detection for:
  - Tools: `.py` files in `tools/` directory
  - Skills: `SKILL.md` files in `skills/*/` subdirectories
  - Schedules: `TASK.md` files in `schedules/*/` subdirectories
- Add new file detection (new tools, skills, or schedules added)
- Add removed file detection (tools, skills, or schedules deleted)
- Re-invoke `build_system_prompt()` when any changes are detected
- Update tool registry, schedule executor, and system prompt cache accordingly

## Capabilities

### New Capabilities

- `workspace-hot-reload`: Detect and apply workspace file changes at runtime without session restart

### Modified Capabilities

None - this is a new capability that extends existing functionality.

## Impact

- `src/psi_agent/session/runner.py`: Add change detection logic before processing user messages
- `src/psi_agent/session/tool_loader.py`: Already has `detect_and_update_tools()` - extend pattern
- `src/psi_agent/session/schedule.py`: Add schedule change detection
- New module: `src/psi_agent/session/workspace_watcher.py` for unified change detection
- System prompt cache invalidation in `SessionRunner`
