## Context

CLAUDE.md specifies that all imports must be placed at file header following the order: stdlib → third-party → local. Some test files had imports inside function bodies, which violates this convention.

## Goals / Non-Goals

**Goals:**
- Move all function-body imports to file headers
- Ensure import order follows CLAUDE.md specification

**Non-Goals:**
- Refactor other code style issues
- Change test logic or behavior

## Decisions

- Move imports to file header: This is the standard Python convention and matches CLAUDE.md requirements
- No `# noqa` comments needed: The imports are legitimate and should be at module level

## Risks / Trade-offs

- None: This is a pure refactoring with no behavior change
