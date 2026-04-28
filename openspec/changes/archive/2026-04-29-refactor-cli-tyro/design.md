## Context

Current implementation uses argparse for subcommand routing in `__main__.py`. This creates friction:
- No intermediate help support (`psi-agent ai --help` fails)
- Manual sys.argv manipulation to delegate to tyro-based CLIs
- Inconsistent with the tyro-based individual CLIs

The project already uses tyro for all individual CLIs, and tyro supports nested subcommands via Union types.

## Goals / Non-Goals

**Goals:**
- Use tyro's native subcommand support for `psi-agent`
- Support help at all levels (`psi-agent --help`, `psi-agent ai --help`, `psi-agent ai openai-completions --help`)
- Move `channel/cli.py` to `channel/cli/cli.py` for consistency
- Maintain backward compatibility with individual CLI scripts

**Non-Goals:**
- Change CLI argument names or behavior
- Remove individual CLI entry points (psi-ai-openai-completions, etc.)

## Decisions

### Use tyro Union Types for Subcommands

**Rationale:** tyro supports nested subcommands through Union types. We can dynamically build a Union of all component CLIs.

**Implementation:**
```python
# Each component exposes a CLI class or function
# __main__.py builds a Union type dynamically
CLI = (
    AiCommands
    | ChannelCommands
    | SessionCommands
    | WorkspaceCommands
)
tyro.cli(CLI)
```

### Component CLI Structure

Each component package exposes a `Commands` class or a callable in its `__init__.py`:

```python
# psi_agent/ai/__init__.py
class Commands:
    """AI provider commands."""
    openai_completions: OpenAICompletionsCommands
    anthropic_messages: AnthropicMessagesCommands
```

**Alternative considered:** Keep CLI functions as-is and wrap them. Rejected because it requires complex wrapper logic and loses tyro's native help generation.

### channel/cli.py Relocation

Move `channel/cli.py` to `channel/cli/cli.py` to match the pattern used by other components (ai, workspace). This makes the discovery logic consistent.

## Risks / Trade-offs

**Risk:** Dynamic Union type construction may have edge cases
→ **Mitigation:** Test thoroughly with all component combinations

**Trade-off:** Requires modifying all CLI modules to expose a consistent interface
→ **Acceptable:** This is a one-time refactor that improves consistency
