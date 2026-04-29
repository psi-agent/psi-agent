## Context

The README files (README.md for English and README_zh.md for Chinese) are the primary entry point for new users. The Quick Start section currently has imprecise descriptions that could confuse users about the component roles and available resources.

## Goals / Non-Goals

**Goals:**
- Improve clarity of Quick Start step descriptions
- Guide users to existing example workspaces
- Ensure terminology consistency (using "AI provider" consistently)
- Maintain parity between English and Chinese versions

**Non-Goals:**
- Restructure the README format
- Add new documentation sections
- Change any code behavior

## Decisions

1. **Reference examples in Step 1**: Add a note pointing to `examples/` directory with the two available workspaces (`a-simple-bash-only-workspace` and `an-openclaw-like-workspace`) so users know they can use or reference these.

2. **Step 2 wording**: Change from "Start the session with an AI provider" to "Start the session" since this step only starts the session component.

3. **Step 3 wording**: Change from "Start an AI component" to "Start an AI provider" for terminology consistency with the project's vocabulary.

4. **Step 4 wording**: Change from "interact with your agent" to "interact with your agent session" to clarify that the channel communicates with the session component.

## Risks / Trade-offs

- **Minimal risk**: This is a documentation-only change with no code impact
- **Translation sync**: Must ensure both English and Chinese versions are updated identically
