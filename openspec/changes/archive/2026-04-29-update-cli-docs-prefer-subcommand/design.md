## Context

psi-agent now has two CLI interfaces:
1. **Unified subcommand interface**: `psi-agent <component> <subcommand>` (e.g., `psi-agent ai openai-completions`)
2. **Standalone commands**: `psi-<component>-<subcommand>` (e.g., `psi-ai-openai-completions`)

The unified interface was introduced to support `uvx psi-agent` without requiring repository clone. Both interfaces work identically, but documentation currently shows standalone commands as primary examples.

Current state:
- README.md Quick Start uses standalone commands
- CLAUDE.md examples use standalone commands
- central-cli spec mentions equivalence but doesn't state preference
- user-readme spec doesn't mention unified interface

## Goals / Non-Goals

**Goals:**
- Document both CLI interfaces clearly
- State that subcommand interface is preferred
- Update all examples in README and CLAUDE.md to use subcommand style
- Update specs to reflect preference

**Non-Goals:**
- Remove standalone commands (they remain for backward compatibility)
- Change any CLI behavior
- Update tests (no functional changes)

## Decisions

### Decision 1: Subcommand interface is preferred

**Rationale:**
- Works with `uvx psi-agent` without cloning repository
- Single entry point is easier to discover
- Consistent with modern CLI patterns (e.g., `git`, `docker`)
- Better for users who just want to try the tool

**Alternatives considered:**
- Keep standalone as preferred: Doesn't support uvx workflow well
- Remove standalone entirely: Breaking change, unnecessary

### Decision 2: Keep standalone commands documented

**Rationale:**
- Backward compatibility
- Some users may prefer shorter commands
- Useful in scripts where subcommand nesting is verbose

## Risks / Trade-offs

- **Risk: User confusion about which to use** → Mitigation: Clear documentation stating preference
- **Risk: Existing docs/tutorials become outdated** → Mitigation: Both interfaces work, just preference change
