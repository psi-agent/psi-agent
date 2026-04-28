## Context

The main branch introduced a new CLI architecture using tyro's native subcommand mechanism. All CLI commands now use dataclass-based implementations with `__call__` methods, and are integrated into a hierarchical command structure (`psi-agent channel telegram`).

The telegram channel CLI was updated to follow this pattern, but the spec was not updated to reflect these changes.

## Goals / Non-Goals

**Goals:**
- Update spec to document tyro dataclass CLI pattern
- Document subcommand integration requirements

**Non-Goals:**
- No code changes - implementation already complete
- No changes to telegram channel functionality

## Decisions

### 1. Add ADDED Requirements section to spec

Since this is adding new requirements without modifying existing ones, use `## ADDED Requirements` section.

### 2. Follow tyro-cli spec pattern

The new requirements should mirror the patterns established in `openspec/specs/tyro-cli/spec.md`.

## Risks / Trade-offs

None - this is a documentation-only change.
