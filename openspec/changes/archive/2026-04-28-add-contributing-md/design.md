## Context

The psi-agent project needs a CONTRIBUTING.md file to guide contributors. The project already has comprehensive coding standards in CLAUDE.md, and uses Claude Code for development. This is a documentation-only change with no code modifications.

## Goals / Non-Goals

**Goals:**
- Provide clear contribution guidelines
- Direct contributors to use Claude Code for PR implementation
- Reference CLAUDE.md as the source of truth for standards

**Non-Goals:**
- Defining code review processes
- Creating detailed development setup instructions
- Establishing CI/CD contribution requirements

## Decisions

1. **Keep CONTRIBUTING.md minimal**: The file will contain only essential information - a brief welcome for issues/PRs, the requirement to use Claude Code for PRs, and a reference to CLAUDE.md. This avoids duplication and keeps the single source of truth in CLAUDE.md.

2. **Clear stance on PR authorship**: Explicitly state that human-written PR code is not accepted. All PRs must be implemented using Claude Code, which will read and follow CLAUDE.md standards automatically.

## Risks / Trade-offs

- **Risk**: Contributors unfamiliar with Claude Code may be discouraged
  → **Mitigation**: The guideline is clear upfront, saving everyone time