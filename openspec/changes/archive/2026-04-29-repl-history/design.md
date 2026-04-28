## Context

The REPL channel currently uses `prompt-toolkit`'s `InMemoryHistory` for input history management. This means:
- History is only available during the current session
- History is lost when the REPL exits
- Users cannot recall inputs from previous sessions

The user wants persistent history stored in the platform's cache directory (`~/.cache/psi-agent/`).

## Goals / Non-Goals

**Goals:**
- Persist REPL input history across sessions
- Store history in `~/.cache/psi-agent/repl_history.txt`
- Use prompt-toolkit's built-in `FileHistory` for automatic file management
- Allow optional configuration of history file path

**Non-Goals:**
- History search/filtering features
- History size limits (use prompt-toolkit defaults)
- Multiple history files per workspace

## Decisions

### Use `FileHistory` from prompt-toolkit

**Rationale:** prompt-toolkit provides `FileHistory` class that automatically handles:
- Appending new entries to file
- Reading history on startup
- Thread-safe file access

**Alternative considered:** Custom file-based history implementation would require more code and could introduce bugs.

### Default history path: `~/.cache/psi-agent/repl_history.txt`

**Rationale:**
- Follows XDG Base Directory Specification (using `~/.cache` for cache files)
- Creates a dedicated `psi-agent` subdirectory for organization
- Simple text file format compatible with prompt-toolkit

**Alternative considered:** `~/.local/share/psi-agent/` - but history is cache data, not user data.

### No history size limit

**Rationale:** prompt-toolkit's `FileHistory` doesn't have built-in size limits. Adding this would require custom implementation. Can be added later if needed.

## Risks / Trade-offs

- **History file grows unbounded** → Can add size limit in future iteration
- **File permissions issues** → Use standard user cache directory with appropriate permissions
- **Concurrent REPL sessions** → prompt-toolkit handles file locking; last write wins
