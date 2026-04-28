## Context

The `ty` type checker reports an error when calling `tyro.cli()` with a Union of Annotated types. This is a known limitation - tyro's type stubs don't have an overload that matches this pattern, even though it works correctly at runtime.

## Goals / Non-Goals

**Goals:**
- Make `ty check` pass without errors
- Use minimal, targeted type ignore comment

**Non-Goals:**
- Refactor the CLI structure
- Change any runtime behavior

## Decisions

### Use `# type: ignore[no-matching-overload]`

Add a targeted type ignore comment on the specific line that triggers the error.

**Rationale:** This is the minimal fix that suppresses the false positive without affecting other type checking. The error code `no-matching-overload` is specific to this issue.

**Alternatives considered:**
- Cast the type: Would obscure the actual type and make the code harder to read
- Refactor to avoid Union: Would require significant changes to the CLI structure for a type checker limitation

## Risks / Trade-offs

None - this is a straightforward type annotation fix with no runtime impact.
