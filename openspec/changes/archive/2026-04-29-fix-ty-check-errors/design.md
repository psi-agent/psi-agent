## Context

The ty type checker is reporting false positive errors in two locations. These errors occur because:

1. **tyro overload complexity**: The `tyro.cli()` function uses sophisticated overload patterns with `TypeForm` and Union types that ty cannot fully resolve. The code is correct, but ty's type inference cannot match the complex overload signatures.

2. **AsyncGenerator union type**: The return type `AsyncGenerator[str] | dict[str, Any]` is a valid union, but ty cannot determine that the runtime check ensures only the AsyncGenerator branch is used in the iteration context.

## Goals / Non-Goals

**Goals:**
- Suppress false positive ty errors with documented `# ty: ignore` comments
- Ensure `ty check` passes cleanly
- Document why each suppression is necessary

**Non-Goals:**
- Refactor code to avoid the type patterns (they are correct)
- Change tyro usage patterns
- Modify the streaming response handling logic

## Decisions

### Decision 1: Use inline `# ty: ignore` comments

**Rationale**: Inline suppression is the standard approach for false positives in type checkers. It keeps the suppression close to the code and documents the specific error being suppressed.

**Alternatives considered**:
- Global ty configuration: Would suppress all errors of a type, including legitimate ones
- Refactoring code: Would add complexity without benefit

### Decision 2: Suppress specific error codes

**Rationale**: Using specific error codes (e.g., `# ty: ignore[no-matching-overload]`) is more precise than blanket suppression.

## Risks / Trade-offs

### Risk: Future ty improvements may make suppressions unnecessary
**Mitigation**: Document the reason for each suppression; revisit when ty is updated

### Risk: Suppression may hide legitimate errors
**Mitigation**: Use specific error codes; only suppress known false positives
