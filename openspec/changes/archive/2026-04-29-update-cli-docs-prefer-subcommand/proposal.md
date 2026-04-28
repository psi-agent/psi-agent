## Why

The CLI documentation currently uses standalone commands (e.g., `psi-ai-openai-completions`) as the primary examples, but the unified subcommand interface (`psi-agent ai openai-completions`) is now the preferred way. Documentation needs to be updated to reflect this preference and clearly explain both interfaces.

## What Changes

- Update README.md to document both CLI interfaces with subcommand style as preferred
- Update README_zh.md (if exists) with same changes
- Update CLAUDE.md examples to use subcommand style
- Update central-cli spec to clarify subcommand is preferred over standalone commands
- Add clear explanation of both interfaces and when to use each

## Capabilities

### New Capabilities

None - this is documentation update only.

### Modified Capabilities

- `central-cli`: Add requirement that subcommand interface is preferred
- `user-readme`: Update to document both CLI interfaces with preference guidance

## Impact

- **Affected files**: README.md, README_zh.md, CLAUDE.md, openspec/specs/central-cli/spec.md, openspec/specs/user-readme/spec.md
- **User impact**: Clearer documentation on which CLI interface to use
- **No breaking changes**: Both interfaces continue to work
