## Why

The current `__main__.py` implementation uses argparse for subcommand routing, which has limitations:
1. No support for intermediate help (e.g., `psi-agent ai --help` doesn't work)
2. Inconsistent with individual CLIs that use tyro
3. Requires manual sys.argv manipulation to delegate to subcommands

Additionally, `channel/cli.py` doesn't follow the same structure as other components (should be `channel/cli/cli.py` for consistency).

## What Changes

- Refactor `__main__.py` to use tyro's native subcommand support instead of argparse
- Move `channel/cli.py` to `channel/cli/cli.py` for consistency with other components
- Update all CLI modules to expose a callable (function or class) compatible with tyro subcommands
- Update specs and README documentation to reflect the new structure

## Capabilities

### New Capabilities

- `tyro-cli`: Unified CLI using tyro's native subcommand mechanism with full help support at all levels

### Modified Capabilities

- `central-cli`: Change from argparse-based to tyro-based implementation
- `channel-cli`: Move from `channel/cli.py` to `channel/cli/cli.py`

## Impact

- `src/psi_agent/__main__.py` - Complete rewrite using tyro
- `src/psi_agent/channel/cli.py` → `src/psi_agent/channel/cli/cli.py`
- `pyproject.toml` - Update script entry for channel-cli
- All `cli.py` files - May need interface adjustments for tyro compatibility
- `openspec/specs/central-cli/spec.md` - Update to reflect new behavior
- `README.md`, `README_zh.md` - Update if command structure changes
