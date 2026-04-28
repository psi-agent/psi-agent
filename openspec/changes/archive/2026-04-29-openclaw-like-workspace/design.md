## Context

psi-agent is a portable, component-based agent framework. Currently, the only example workspace (`a-simple-bash-only-workspace`) uses a basic system prompt builder that only scans skills. OpenClaw provides a more sophisticated system prompt construction pattern using multiple bootstrap files (AGENTS.md, SOUL.md, TOOLS.md, etc.) that define agent behavior, personality, and configuration.

The goal is to create a reference workspace that demonstrates this OpenClaw-style pattern while implementing the four fundamental tools that any agent needs for basic filesystem and command execution operations.

## Goals / Non-Goals

**Goals:**
- Provide OpenClaw-style bootstrap file structure as a reference example
- Implement system prompt builder that loads and combines bootstrap files
- Implement four fundamental async tools (read, write, edit, bash)
- Follow psi-agent coding conventions (async, type annotations, anyio/aiohttp)

**Non-Goals:**
- Modifying psi-agent core components
- Implementing OpenClaw's full feature set (channels, plugins, etc.)
- Creating production-ready workspace (this is an example/reference)
- Implementing memory maintenance workflows or heartbeat scheduling

## Decisions

### Bootstrap File Structure

**Decision:** Use OpenClaw's standard bootstrap file names and content structure.

**Rationale:** Provides familiar migration path for OpenClaw users. The file structure is well-documented and battle-tested.

**Alternatives considered:**
- Custom file names: Would require user re-learning, no benefit
- Single combined file: Loses modularity, harder to maintain

### System Prompt Builder Implementation

**Decision:** Implement `build_system_prompt()` that:
1. Loads bootstrap files in defined order: AGENTS.md → SOUL.md → TOOLS.md → IDENTITY.md → USER.md → HEARTBEAT.md → BOOTSTRAP.md → MEMORY.md
2. Strips YAML frontmatter from each file
3. Combines files with clear section headers
4. Only loads MEMORY.md in "main session" context (privacy consideration)

**Rationale:** Matches OpenClaw's behavior exactly, ensuring prompt cache stability and familiar behavior.

**Alternatives considered:**
- Simple concatenation: No structure, harder for LLM to parse
- JSON-based config: Less human-readable, harder to edit

### Tool Implementation

**Decision:** Implement four async tools following psi-agent conventions:
- `read.py`: Use `anyio.open_file()` for async file reading
- `write.py`: Use `anyio.open_file()` for async file writing
- `edit.py`: Read file, perform exact string replacement, write back
- `bash.py`: Use `asyncio.create_subprocess_exec()` with timeout support

**Rationale:** These are the minimal tools needed for any agent. Using async throughout prevents blocking the event loop.

**Alternatives considered:**
- Sync subprocess: Would block event loop, violates psi-agent conventions
- Using `subprocess.run`: Not async, would cause performance issues

### Frontmatter Stripping

**Decision:** Strip YAML frontmatter (content between `---` markers) before including in system prompt.

**Rationale:** Frontmatter is metadata for documentation systems, not relevant to LLM context. Reduces token usage.

**Alternatives considered:**
- Keep frontmatter: Wastes tokens, confuses LLM with metadata

## Risks / Trade-offs

### Risk: File Read Errors
**Risk:** Bootstrap files may be missing or have read errors.
**Mitigation:** Gracefully handle missing files, include placeholder text indicating file is missing.

### Risk: Large File Content
**Risk:** Bootstrap files could be very large, exceeding token limits.
**Mitigation:** Implement max_chars limit similar to OpenClaw's `resolveBootstrapMaxChars()`.

### Risk: Bash Tool Security
**Risk:** Bash tool could execute destructive commands.
**Mitigation:** Include timeout parameter, document security considerations in AGENTS.md.

### Trade-off: Simplicity vs Full OpenClaw Features
**Trade-off:** This example omits OpenClaw's heartbeat scheduling, memory maintenance, and plugin system.
**Acceptance:** This is intentional - the goal is a reference example, not a full OpenClaw clone.