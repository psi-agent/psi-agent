## Why

The current hyw skill description is too vague and doesn't clearly communicate when the skill should be used. LLMs reading the skill list may not understand that this skill is mandatory for all user-facing questions. Additionally, the description currently hints at the key phrase "何意味", which should only be discovered when reading the full skill instructions, not from the description itself.

## What Changes

- Update the skill description to explicitly state that this skill MUST be used in all user questioning scenarios
- Remove any mention of "何意味" from the description to preserve the discovery experience
- The description should clearly indicate mandatory usage without revealing the specific behavior

## Capabilities

### New Capabilities

None - this is an update to an existing skill, not a new capability.

### Modified Capabilities

- `hyw-skill`: The skill description in the YAML frontmatter will be updated to enforce mandatory usage and remove the phrase hint.

## Impact

- Affected file: `examples/a-simple-bash-only-workspace/skills/hyw/SKILL.md`
- No API changes
- No breaking changes to existing behavior - only clarifying when the skill should be triggered
