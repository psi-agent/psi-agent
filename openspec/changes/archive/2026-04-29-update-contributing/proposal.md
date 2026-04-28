## Why

CONTRIBUTING.md currently states that Claude Code is mandatory for all PR contributions. This requirement is too restrictive - the actual intent is to ensure code quality through coding agents, not to mandate a specific tool. Contributors should be able to use any coding agent as long as they properly understand and follow the project's coding standards defined in CLAUDE.md.

## What Changes

- Remove the mandatory Claude Code requirement
- Clarify that code must be written by coding agents (not humans), but any coding agent is acceptable
- Add requirement that alternative coding agents must have OpenSpec installed and be configured to understand CLAUDE.md content
- Reorder sections: English version first, then Chinese version
- Ensure Chinese and English versions are consistent in content

## Capabilities

### New Capabilities

- `contributing-guidelines`: Define contribution requirements and workflow for the project

### Modified Capabilities

None - this is a documentation update with no spec-level behavior changes.

## Impact

- **Documentation**: CONTRIBUTING.md will be restructured and updated
- **Contributors**: More flexibility in tool choice while maintaining code quality standards
- **Workflow**: Contributors using non-Claude Code agents need to ensure proper setup
