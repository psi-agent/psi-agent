## Context

The simple workspace example (`examples/a-simple-bash-only-workspace/`) has a `build_system_prompt()` function that generates the system prompt for the agent. Currently, it shows the workspace directory path but doesn't explicitly mention where skills are located.

## Goals / Non-Goals

**Goals:**
- Add explicit guidance about the skills directory location in the system prompt
- Make it clear to the agent that all skills are stored in `workspace/skills/`

**Non-Goals:**
- Changing the workspace structure
- Modifying any other workspace examples
- Adding new features beyond the informational message

## Decisions

- **Placement**: Add the skills directory information in the "Workspace" section of the system prompt, right after the workspace directory path. This keeps related information together.
- **Format**: Use a simple sentence format that clearly states the location and purpose of the skills directory.

## Risks / Trade-offs

No significant risks. This is a minor informational change that improves clarity without affecting behavior.
