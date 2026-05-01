## Why

The current system prompt in the simple workspace example tells the agent about the workspace directory but doesn't explicitly inform the agent where skills are located. This makes it unclear to the agent that all skills are stored in the `skills/` subdirectory within the workspace, which could lead to confusion when the agent tries to read skill details.

## What Changes

- Add a sentence in the system prompt that explicitly states the skills directory location
- Inform the agent that all skills are stored in the `skills/` directory within the workspace

## Capabilities

### New Capabilities

- `skill-directory-guidance`: Provides explicit guidance to the agent about where skills are located in the workspace structure

### Modified Capabilities

None - this is a new informational addition, not a behavior change.

## Impact

- `examples/a-simple-bash-only-workspace/systems/system.py` - modification to `build_system_prompt()` function
- No API changes
- No breaking changes
