## Context

The session module's CLAUDE.md provides comprehensive documentation for developers working on psi-session. After the recent code quality improvements (extracting `_parse_streaming_response` helper method), the documentation should be updated to reflect the current architecture.

The current documentation covers:
- Architecture overview
- Module structure and responsibilities
- Core data structures
- Message processing flows
- Tool system
- Workspace hot-reload
- Schedule system
- History persistence
- System interface
- HTTP interface
- CLI usage

## Goals / Non-Goals

**Goals:**
- Update runner.py module description to mention the streaming parsing helper
- Ensure documentation reflects current architecture accurately
- Maintain consistent level of detail across all sections

**Non-Goals:**
- Rewriting or restructuring the entire document
- Adding new sections that don't relate to recent changes
- Changing any code behavior

## Decisions

### Update runner.py module description

**Decision**: Add a brief mention of the `_parse_streaming_response` helper method in the module responsibilities table.

**Rationale**: The helper method is a key architectural improvement that centralizes SSE parsing logic. Developers should know it exists when reading the module overview.

### Keep documentation at consistent detail level

**Decision**: Only add minimal updates to maintain consistency with existing documentation style.

**Rationale**: The existing documentation provides good overview-level information. Adding too much detail about internal methods would create inconsistency with other modules' documentation.

## Risks / Trade-offs

**Documentation becoming outdated again**: Future code changes may not update docs.
→ Mitigation: Keep updates minimal and focused on architectural decisions that are unlikely to change frequently.
