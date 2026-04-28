## Context

psi-session currently loads workspace files (tools, skills, schedules) only at startup:

1. **Tools**: Loaded in `SessionRunner.__aenter__()` via `load_all_tools()`, with `detect_and_update_tools()` called per-request but only checking for new/removed/modified tool files
2. **Skills**: Loaded indirectly via `build_system_prompt()` which scans `skills/*/SKILL.md` files
3. **Schedules**: Loaded in `SessionServer.start()` via `load_schedules()`, then started with `ScheduleExecutor`

The system prompt is cached in `SessionRunner._system_prompt_cache` and never refreshed.

**Current State:**
- `detect_and_update_tools()` already exists and handles tool hot-reload via MD5 hash comparison
- No equivalent for skills or schedules
- System prompt is built once and cached

## Goals / Non-Goals

**Goals:**
- Detect changes to tools, skills, and schedules on every user message
- Use file hash (MD5) to detect modifications
- Detect new files (new tools, skills, schedules)
- Detect removed files (deleted tools, skills, schedules)
- Re-invoke `build_system_prompt()` when skills or schedules change
- Update tool registry when tools change
- Update schedule executor when schedules change

**Non-Goals:**
- File system watching (inotify, watchdog) - we use polling on each request
- Hot-reload of `systems/system.py` itself - requires module reload complexity
- Partial updates - we rebuild affected components entirely

## Decisions

### 1. Polling on Each Request vs File System Watching

**Decision:** Poll on each user message (check file hashes before processing).

**Rationale:**
- Simpler implementation, no external dependencies
- Works across all platforms (Linux, macOS, Windows)
- No background threads or event loops needed
- Low overhead: only computes hashes when a request arrives
- Consistent with existing `detect_and_update_tools()` pattern

**Alternatives Considered:**
- inotify/watchdog: More complex, platform-specific, requires background thread
- Timer-based polling: Unnecessary overhead when idle

### 2. Unified Workspace Watcher Module

**Decision:** Create a new `workspace_watcher.py` module that provides unified change detection for all workspace file types.

**Rationale:**
- Single responsibility for change detection
- Reusable across tools, skills, schedules
- Easy to test in isolation
- Follows existing module structure

### 3. Hash Storage Strategy

**Decision:** Store file hashes in memory within the watcher component.

**Rationale:**
- No persistence needed - hashes are only relevant within a session
- Fast comparison
- Consistent with existing `ToolSchema.file_hash` pattern

### 4. System Prompt Rebuild Trigger

**Decision:** Rebuild system prompt when skills or schedules change, not when tools change.

**Rationale:**
- Skills are embedded in system prompt via `_build_skills_section()`
- Schedules are separate from system prompt but need schedule executor update
- Tools are already handled by existing `detect_and_update_tools()`

## Risks / Trade-offs

### Risk: Hash Computation Overhead
**Mitigation:** Hash computation is fast (MD5), only runs on request, and only for files that exist. For typical workspaces (< 100 files), overhead is negligible (< 10ms).

### Risk: Race Condition During File Edit
**Mitigation:** If a file is being written while a request arrives, we might read a partial file. This is acceptable - the next request will detect the change again. Could add retry logic if needed.

### Risk: Module Reload Complexity for system.py
**Mitigation:** We explicitly exclude `systems/system.py` from hot-reload. If users need to update system.py, they must restart the session. This is documented as a known limitation.

### Trade-off: No Immediate Feedback
The user won't know if hot-reload happened. We log changes at INFO level for visibility.
