## Context

The psi-session component receives a workspace path from the CLI as a string. This path can be relative (e.g., `./workspace`) or absolute (e.g., `/home/user/workspace`). Currently, the path is stored as-is and converted to `anyio.Path` when accessed via `workspace_path()`, but is never resolved to an absolute path.

The problem manifests when:
1. User starts session with a relative workspace path (e.g., `--workspace ./my-workspace`)
2. The session's current working directory may differ from where the workspace actually exists
3. The System class in systems/system.py uses `self._workspace_dir / "skills"` to find skills
4. The WorkspaceWatcher uses `self.workspace / "skills"` to watch for changes
5. All these lookups may fail or look in the wrong location if cwd doesn't match the intended workspace location

## Goals / Non-Goals

**Goals:**
- Ensure workspace paths are always resolved to absolute paths at initialization
- Maintain backward compatibility - relative paths should still work as input
- Keep the fix minimal and focused on the config layer

**Non-Goals:**
- Changing CLI behavior or adding validation for non-existent paths
- Modifying workspace component behavior (pack, mount, etc.)
- Adding path resolution in the System class (it should receive already-resolved paths)

## Decisions

### Decision 1: Resolve path in `SessionConfig.workspace_path()`

**Choice:** Make `workspace_path()` an async method that resolves the path to absolute.

**Alternatives considered:**
1. Resolve in CLI before passing to SessionConfig - rejected because it adds complexity to CLI layer and doesn't fix internal callers
2. Resolve in SessionRunner initialization - rejected because multiple components use `workspace_path()` and they should all get the same resolved path
3. Resolve in `SessionConfig.__post_init__` - rejected because dataclass `__post_init__` is synchronous and `anyio.Path.resolve()` is async

**Rationale:** The config's `workspace_path()` method is the single source of truth for all workspace path access. Making it async and resolving there ensures all callers get the absolute path without duplicating resolution logic.

### Decision 2: Update all callers to use `await config.workspace_path()`

**Choice:** Update `SessionRunner`, `SessionServer`, and related code to await the async method.

**Rationale:** This is a necessary consequence of Decision 1. The change is localized and straightforward.

### Decision 3: Cache the resolved path in SessionConfig

**Choice:** Cache the resolved `anyio.Path` after first resolution to avoid repeated async calls.

**Rationale:** The workspace path doesn't change during a session's lifetime. Caching improves efficiency and ensures consistency across all accesses.

## Risks / Trade-offs

**Risk: Breaking existing sync callers** → Mitigation: All current callers are already in async contexts (SessionRunner, WorkspaceWatcher initialization). No sync callers exist.

**Risk: Performance impact of async resolution** → Mitigation: Resolution happens once at startup and is cached. Negligible overhead.

**Risk: Relative symlinks resolution** → Mitigation: `anyio.Path.resolve()` resolves symlinks and relative components correctly, following Python's standard behavior.