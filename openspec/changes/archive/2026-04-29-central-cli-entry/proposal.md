## Why

Currently, psi-agent components have separate CLI entry points (e.g., `psi-ai-chat-completions`, `psi-channel-cli`). This works well for development but creates friction for `uvx` users who want to run the agent directly without cloning the repository. A central entry point allows `uvx psi-agent <subcommand>` to work seamlessly.

## What Changes

- Add `psi_agent/__main__.py` as the central CLI entry point
- Add `psi-agent` script entry in `pyproject.toml`
- Implement dynamic subcommand discovery based on existing package structure
- Update README.md and README_CN.md with brief mention of this interface

## Capabilities

### New Capabilities

- `central-cli`: Unified CLI entry point that dynamically discovers and delegates to component CLIs based on package structure

### Modified Capabilities

- None (this is a new interface, existing individual CLIs remain unchanged)

## Impact

- New file: `src/psi_agent/__main__.py`
- Modified: `pyproject.toml` (add script entry)
- Modified: `README.md`, `README_CN.md` (brief documentation)
- No changes to existing component CLIs - they remain as standalone entry points
