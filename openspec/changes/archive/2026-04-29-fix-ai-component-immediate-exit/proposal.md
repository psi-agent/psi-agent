## Why

All standalone CLI entry points (e.g., `psi-ai-openai-completions`, `psi-session`, `psi-channel-*`, `psi-workspace-*`) immediately exit without executing any code. This is caused by a bug introduced during the recent CLI refactor: `tyro.cli()` returns a callable dataclass instance but the code never calls it.

The unified `psi-agent` CLI works correctly because `__main__.py` explicitly calls the result: `result()`. However, all standalone entry points defined in `pyproject.toml` are broken.

## What Changes

- Fix all standalone CLI `main()` functions to call the returned object from `tyro.cli()`
- Affected entry points:
  - `psi-ai-openai-completions`
  - `psi-ai-anthropic-messages`
  - `psi-session`
  - `psi-channel-cli`
  - `psi-channel-repl`
  - `psi-channel-telegram`
  - `psi-workspace-pack`
  - `psi-workspace-unpack`
  - `psi-workspace-mount`
  - `psi-workspace-umount`
  - `psi-workspace-snapshot`

## Capabilities

### New Capabilities

None - this is a bug fix, no new capabilities are introduced.

### Modified Capabilities

None - this is a bug fix at the implementation level, no spec-level behavior changes.

## Impact

- **Affected files**: All CLI modules in `src/psi_agent/`
- **User impact**: Standalone commands like `uv run psi-ai-openai-completions` will work again
- **No breaking changes**: The fix restores expected behavior
