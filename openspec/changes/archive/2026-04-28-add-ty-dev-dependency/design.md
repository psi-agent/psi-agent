## Context

CI workflow runs `uv run ty check` for type checking, but `ty` is not installed because it's missing from dev dependencies in pyproject.toml.

## Goals / Non-Goals

**Goals:**
- Fix CI type check step by installing `ty`

**Non-Goals:**
- Changing type checking configuration
- Adding other type checkers

## Decisions

### Add ty to dev dependencies

**Rationale:** `ty` is Astral's new type checker (same team as ruff/uv). It's fast and integrates well with the existing toolchain.

## Risks / Trade-offs

- **ty availability:** ty is newer and may have fewer checks than pyright → acceptable for CI purposes