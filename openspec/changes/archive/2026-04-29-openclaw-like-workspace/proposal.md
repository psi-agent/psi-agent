## Why

psi-agent needs a reference workspace example that demonstrates the OpenClaw-style system prompt construction pattern. This provides a familiar starting point for users migrating from OpenClaw and establishes a standard for how system prompts should be built in psi-agent workspaces. Additionally, psi-agent lacks the four fundamental tools (read, write, edit, bash) that are essential for any agent to interact with the filesystem and execute commands.

## What Changes

- Add `examples/an-openclaw-like-workspace/` directory with OpenClaw-style bootstrap files:
  - `AGENTS.md` - Main workspace configuration and behavior rules
  - `SOUL.md` - Agent personality and behavioral guidelines
  - `TOOLS.md` - Local notes for environment-specific configuration
  - `IDENTITY.md` - Agent identity record (name, creature, vibe, emoji)
  - `USER.md` - User profile information
  - `BOOTSTRAP.md` - First-run initialization ritual
  - `HEARTBEAT.md` - Periodic check configuration
  - `MEMORY.md` - Long-term memory storage
- Implement OpenClaw-style system prompt builder in `systems/system.py`:
  - Load all bootstrap files in defined order
  - Strip YAML frontmatter from file contents
  - Combine files into coherent system prompt
  - Support memory file loading with privacy considerations
- Implement four fundamental tools in `tools/`:
  - `read.py` - Async file reading
  - `write.py` - Async file writing
  - `edit.py` - Async file editing with exact string replacement
  - `bash.py` - Async shell command execution

## Capabilities

### New Capabilities

- `openclaw-system-prompt`: OpenClaw-style system prompt construction that loads AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md, and MEMORY.md files in a defined order, strips frontmatter, and combines them into the system prompt
- `fundamental-tools`: Four core tools (read, write, edit, bash) that provide essential filesystem and command execution capabilities for any agent workspace

### Modified Capabilities

- None (this is a new example workspace, not modifying existing specs)

## Impact

- New example workspace: `examples/an-openclaw-like-workspace/`
- New tools: `examples/an-openclaw-like-workspace/tools/{read,write,edit,bash}.py`
- New system prompt builder: `examples/an-openclaw-like-workspace/systems/system.py`
- No changes to existing psi-agent core code
- Provides reference implementation for OpenClaw users migrating to psi-agent
