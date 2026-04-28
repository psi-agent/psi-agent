## Context

CLAUDE.md serves as the developer guide for the project. Currently, the "启动命令示例" section shows commands like `psi-agent session ...` without explaining that during development, `uv run` prefix is needed.

Developers working on the project typically:
1. Clone the repository
2. Run commands with `uv run psi-agent ...` during development
3. Use `psi-agent ...` directly only after installing the package

## Goals / Non-Goals

**Goals:**
- Add `uv run` prefix to CLI examples in CLAUDE.md
- Explain when to use `uv run` vs direct command

**Non-Goals:**
- Change README.md (that's for end users who install the package)
- Change any CLI behavior

## Decisions

### Decision 1: Use `uv run psi-agent ...` in CLAUDE.md examples

**Rationale:**
- CLAUDE.md is for developers working on the project
- During development, `uv run` is the standard way to run commands
- Makes examples directly copy-pasteable for developers

## Risks / Trade-offs

- **Risk: Confusion between README and CLAUDE.md** → Mitigation: Add clear note explaining the difference
