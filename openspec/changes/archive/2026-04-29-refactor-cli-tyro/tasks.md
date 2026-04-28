## 1. Restructure channel CLI

- [x] 1.1 Create `src/psi_agent/channel/cli/` directory
- [x] 1.2 Move `channel/cli.py` to `channel/cli/cli.py`
- [x] 1.3 Update `pyproject.toml` script entry for `psi-channel-cli`
- [x] 1.4 Update `openspec/specs/channel-cli/spec.md` to reflect new command path

## 2. Create Commands classes for each component

- [x] 2.1 Create `Commands` class in `psi_agent/ai/__init__.py` for ai subcommands
- [x] 2.2 Create `Commands` class in `psi_agent/channel/__init__.py` for channel subcommands
- [x] 2.3 Create `Commands` class in `psi_agent/workspace/__init__.py` for workspace subcommands
- [x] 2.4 Expose `Commands` in `psi_agent/session/__init__.py` for session command

## 3. Refactor __main__.py to use tyro

- [x] 3.1 Rewrite `__main__.py` to use tyro's Union type for subcommands
- [x] 3.2 Implement dynamic discovery of Commands classes from component packages
- [x] 3.3 Ensure intermediate help works (`psi-agent ai --help`)

## 4. Update documentation

- [x] 4.1 Update `openspec/specs/central-cli/spec.md` with corrected scenario names

## 5. Verification

- [x] 5.1 Verify `psi-agent --help` displays all components
- [x] 5.2 Verify `psi-agent ai --help` displays ai subcommands
- [x] 5.3 Verify `psi-agent ai openai-completions --help` works correctly
- [x] 5.4 Verify `psi-agent channel cli --help` works correctly
- [x] 5.5 Run lint, format, and type checks
