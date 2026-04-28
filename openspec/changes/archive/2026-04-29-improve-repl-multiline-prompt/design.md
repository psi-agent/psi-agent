## Context

The REPL channel uses prompt-toolkit for input handling with multiline support. Currently, when users enter multi-line input (via Alt+Enter), the continuation lines show only spaces for alignment with the main prompt (`> `). This makes it difficult to visually distinguish that the user is still in multi-line input mode.

## Goals / Non-Goals

**Goals:**
- Add a visible continuation prompt symbol for multi-line input
- Improve user experience by making multi-line mode more obvious

**Non-Goals:**
- Changing the main prompt symbol (`> `)
- Changing the keybindings for multi-line input
- Adding configuration options for prompt symbols

## Decisions

### Decision 1: Use `. ` as continuation prompt

**Choice:** Use `. ` (dot followed by space) as the continuation prompt.

**Rationale:**
- Visually distinct from the main prompt (`> `) while maintaining similar width
- Not easily confused with the main prompt or empty space
- Minimal and unobtrusive
- User selected this option

**Alternatives considered:**
- `... ` (ellipsis) - Python style, but wider
- `| ` (pipe) - Common in shells, but may be confused with pipe operator
- `~ ` (tilde) - Subtle but may be less obvious

### Decision 2: Use prompt-toolkit's prompt_continuation parameter

**Choice:** Use prompt-toolkit's built-in `prompt_continuation` parameter in `prompt_async()`.

**Rationale:**
- Native support in prompt-toolkit
- Simple implementation with no additional dependencies
- Consistent with prompt-toolkit best practices

## Risks / Trade-offs

- **Risk:** The continuation prompt width must match the main prompt width for proper alignment → **Mitigation:** Both `> ` and `. ` are 2 characters, ensuring alignment
