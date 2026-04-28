## Context

psi-agent currently has multiple CLI entry points defined in `pyproject.toml`:
- `psi-ai-chat-completions` → `psi_agent.ai.chat_completions`
- `psi-channel-cli` → `psi_agent.channel.cli`
- `psi-session` → `psi_agent.session`
- `psi-workspace-pack/unpack/mount/umount/snapshot`

Each component has its own `__main__.py` that uses `tyro.cli()` for argument parsing. The package structure follows a convention: `psi_agent.<component>.<subcomponent>` maps to CLI command `<component> <subcomponent>`.

## Goals / Non-Goals

**Goals:**
- Provide a single `psi-agent` entry point for `uvx` users
- Dynamically discover subcommands from package structure
- Maintain backward compatibility with existing individual CLIs
- Keep implementation simple and maintainable

**Non-Goals:**
- Change existing CLI behavior or arguments
- Deprecate individual CLI entry points
- Add complex plugin architecture

## Decisions

### Dynamic Subcommand Discovery via Package Inspection

**Rationale:** Instead of hardcoding subcommands, we inspect `psi_agent` subpackages at runtime. Each subpackage (e.g., `ai`, `channel`, `session`, `workspace`) becomes a subcommand group, and their subpackages become nested subcommands.

**Implementation:**
1. Use `importlib.resources.files()` to list subpackages of `psi_agent`
2. For each subpackage, check if it has a `main()` function or `__main__.py`
3. Use `tyro.cli()` with nested subcommand structure

**Alternative considered:** Entry point registration in `pyproject.toml` - rejected because it requires manual updates when adding new components.

### CLI Structure Convention

Commands follow the pattern: `psi-agent <component> <subcomponent>`

Examples:
- `psi-agent ai chat-completions` → `psi_agent.ai.chat_completions.main()`
- `psi-agent channel cli` → `psi_agent.channel.cli.main()`
- `psi-agent session` → `psi_agent.session.main()`

The convention: replace underscores with hyphens, use dot hierarchy as space-separated commands.

## Risks / Trade-offs

**Risk:** Package inspection may fail in unusual environments (e.g., frozen executables)
→ **Mitigation:** Fall back to a hardcoded list of known components if inspection fails

**Trade-off:** Slight startup overhead for package inspection
→ **Acceptable:** The overhead is minimal (~ms) and only affects CLI startup, not runtime performance
