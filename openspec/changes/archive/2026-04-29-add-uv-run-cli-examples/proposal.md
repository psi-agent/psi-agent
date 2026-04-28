## Why

CLAUDE.md currently shows CLI examples without the `uv run` prefix, but during development the most common way to run commands is `uv run psi-agent ...`. This should be explicitly documented for developers working on the project.

## What Changes

- Update CLAUDE.md "启动命令示例" section to show `uv run psi-agent ...` as the development-time running method
- Explain that `uv run` is used during development, while `psi-agent` (without prefix) is used after installation

## Capabilities

### New Capabilities

None - this is documentation improvement only.

### Modified Capabilities

None - no spec-level behavior changes.

## Impact

- **Affected files**: CLAUDE.md
- **User impact**: Developers will have clearer guidance on how to run commands during development
- **No breaking changes**: Documentation only
