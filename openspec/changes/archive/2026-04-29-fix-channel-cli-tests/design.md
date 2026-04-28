## Context

After refactoring CLI to use tyro, `channel/cli.py` was moved to `channel/cli/cli.py`. The test file `tests/channel/test_cli.py` still imports from the old path, causing import errors.

## Goals / Non-Goals

**Goals:**
- Fix broken test imports
- Maintain consistency with `tests/channel/repl/` structure

**Non-Goals:**
- Change test behavior or add new tests

## Decisions

### Move test file to subdirectory

Move `tests/channel/test_cli.py` to `tests/channel/cli/test_cli.py` to match the source structure (`src/psi_agent/channel/cli/`).

**Rationale:** Consistency with `tests/channel/repl/` which already follows this pattern.

### Update imports

The test file imports `send_message` from `psi_agent.channel.cli`. This needs to be updated to `psi_agent.channel.cli.cli`.

## Risks / Trade-offs

None - this is a straightforward structural fix.
